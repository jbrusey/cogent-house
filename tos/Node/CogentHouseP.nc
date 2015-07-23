// -*- c -*-
module CogentHouseP
{
  uses {
    // Basic Interfaces
    interface Boot;
    interface Leds;
    interface LocalTime<TMilli>;
    interface BlinkStatus;

    // Timers
    interface Timer<TMilli> as SenseTimer;
    interface Timer<TMilli> as SendTimeOutTimer;

    // Radio + CTP
    interface SplitControl as RadioControl;
    interface Send as StateSender;
    interface BootMessage;
    interface StdControl as CollectionControl;
    interface CtpInfo;
    interface LowPowerListening;    

    // Ack interfaces
    interface Crc as CRCCalc;
    interface StdControl as DisseminationControl;
    interface DisseminationValue<AckMsg> as AckValue;

    // Sensing related
    interface Read<bool> as Sensing;
    interface AccessibleBitVector as Configured;
    interface PackState;
    interface TransmissionControl;
  }
}
implementation
{
  uint32_t	sample_period;

  uint8_t	nodeType;	/* default node type is determined by top 4 bits of node_id */
  bool		sending;
  bool		shutdown	     = FALSE;
  bool		first_period_pending = FALSE;
  bool		seen_first_ack	     = FALSE;
  message_t	dataMsg;
  uint16_t	message_size;
  uint8_t	msgSeq		     = 0;
  uint8_t	expSeq		     = 255;
  uint32_t	sense_start_time;
  uint32_t	send_start_time;  
  uint8_t	missedPKT	     = 0;

  bool	        packet_pending       = FALSE;
  float		last_duty            = 0.;
  uint32_t	last_errno           = 1;
  uint32_t	last_transmitted_errno;

  /** prototypes **/
  void radioStop(void);


  event void BootMessage.sendDone(error_t result) { 
    call SenseTimer.startOneShot(DEF_FIRST_PERIOD);
    first_period_pending = FALSE;
  }


  /** powerDown - if the battery voltage goes low, stop everything. 
   */
  task void powerDown(){
    call SenseTimer.stop();
    radioStop();
  }

  /** Restart the sense timer as a one shot. Using a one shot here
      rather than periodic removes the possibility of re-entering the
      sense loop before the last one has finished. The only slight
      problem here is that this may induce a slight drift in when the
      timer fires.

      This method is called both when the send completes (sendDone)
      and when the send times out.
   */
  void restartSenseTimer() {
    uint32_t stop_time = call LocalTime.get();
    uint32_t send_time, next_interval;
    if (!shutdown){
      sending = FALSE;

#ifdef DEBUG
      printf("restartSenseTimer at %lu\n", call LocalTime.get());
      printfflush();
#endif

    //Calculate the next interval
      send_time = subtract_time(stop_time, sense_start_time);
    
      if (sample_period < send_time)
	next_interval = 0;
      else
	next_interval = sample_period - send_time;

#ifdef DEBUG
      printf("startOneShot at %lu\n", call LocalTime.get());
      printf("interval of %lu\n", next_interval);
      printfflush();
#endif
      call SenseTimer.startOneShot(next_interval);
      
    }
  }


  /** reportError records a code to be sent on the next transmission. 
   * @param errno error code
   */
  void reportError(uint8_t errno) {
    uint32_t errno_cubed;
#ifdef DEBUG
    printf("Error message: %u\n", errno);
    printfflush();
#endif
    errno_cubed = errno;
    errno_cubed = errno_cubed * errno_cubed * errno_cubed;
    if (last_errno % errno_cubed != 0)
      last_errno *= errno;
  }


  /********* Data Send Methods **********/

  void packstate_add(int key, float value) {
      if (call PackState.add(key, value) == FAIL)
	reportError(ERR_PACK_STATE_OVERFLOW);
  }

  void sendState()
  {
    packed_state_t ps;
    StateMsg *newData;

    int pslen;
    int i;
    am_addr_t parent;
    
#ifdef DEBUG
    printf("sendState %lu\n", call LocalTime.get());
    printfflush();
#endif
    if (sending) {
      reportError(ERR_SEND_WHILE_SENDING);
      return;
    }
    if (packet_pending) {
      reportError(ERR_SEND_WHILE_PACKET_PENDING);
      return;
    }

    pslen = call PackState.pack(&ps);
    message_size = sizeof (StateMsg) - sizeof newData->packed_state + pslen * sizeof (float);
    newData = call StateSender.getPayload(&dataMsg, message_size);
    if (newData != NULL) { 
      //we're going do a send so pack the msg count and then increment
      newData->timestamp = call LocalTime.get();
      newData->special = SPECIAL;

      //increment and pack seq
      expSeq = msgSeq;
      msgSeq++;
      newData->seq = expSeq;
      newData->rssi = 0.;

      newData->ctp_parent_id = -1;
      if (call CtpInfo.getParent(&parent) == SUCCESS) { 
	newData->ctp_parent_id = parent;
      }
     
      for (i = 0; i < sizeof newData->packed_state_mask; i++) { 
	newData->packed_state_mask[i] = ps.mask[i];
      }
      for (i = 0; i < pslen; i++) {
	newData->packed_state[i] = ps.p[i];
      }
      send_start_time = call LocalTime.get();
      call SendTimeOutTimer.startOneShot(LEAF_TIMEOUT_TIME);

      if (call StateSender.send(&dataMsg, message_size) == SUCCESS) {
#ifdef DEBUG
	printf("sending begun at %lu\n", call LocalTime.get());
	printfflush();
#endif
	sending = TRUE;
      }
    }
  }


  event void StateSender.sendDone(message_t *msg, error_t ok) {
#ifdef DEBUG
    printf("sending done at %lu\n", call LocalTime.get());
    printfflush();
#endif
    if (ok != SUCCESS) {
#ifdef BLINKY
      call Leds.led0Toggle(); 
#endif
      reportError(ERR_SEND_FAILED);
    }
  }



  event void SendTimeOutTimer.fired() {
    sample_period = DEF_SENSE_PERIOD;

#ifdef DEBUG
    printf("ack receiving failed %lu\n", call LocalTime.get());
    printf("Sample Period to be used %lu\n", sample_period);
    printfflush();
#endif
    restartSenseTimer();
  }
  
  /********* Main Loop Methods **********/

  event void Boot.booted(){
#ifdef DEBUG
    printf("Booted %lu\n", call LocalTime.get());
    printfflush();
#endif
    
    call BlinkStatus.start();

    nodeType = TOS_NODE_ID >> 12;
    sample_period = DEF_SENSE_PERIOD;

    // Configure the node for attached sensors.

    call Configured.clearAll();
    call Configured.set(RS_TEMPERATURE);
    call Configured.set(RS_HUMIDITY);
    call Configured.set(RS_ADC_0);
    call Configured.set(RS_ADC_1);
    call Configured.set(RS_ADC_2);


    sending = FALSE;

    // TODO: check that voltage is > X and if not, don't start the radio

    first_period_pending = TRUE;
    call RadioControl.start();
  }

  /* SenseTimer.fired
   *
   * - begin sensing cycle by requesting, in parallel, for all active
   * sensors to start reading.
   */
  event void SenseTimer.fired() {
#ifdef BLINKY
    call Leds.led0Toggle();
#endif
    sense_start_time = call LocalTime.get();
    if (! sending) { 
#ifdef DEBUG
      printf("sensing begun at %lu\n", sense_start_time);
      printfflush();
#endif

      call Sensing.read();

    }
  }

  /** 
   * Sensing.readDone - completion of all sensing; collected data
   * is formatted into the PackState object.
   */
   
  event void Sensing.readDone(error_t result, bool overflow) { 
    if (result == SUCCESS) {       
      if (last_errno != 1)
	packstate_add(SC_ERRNO, (float) last_errno);
      last_transmitted_errno = last_errno;

      sendState();
    }
    else
      restartSenseTimer();
      
    if (overflow)
      reportError(ERR_PACK_STATE_OVERFLOW);

  }

  /*********** Radio Control *****************/

  event void RadioControl.startDone(error_t ok) {
    if (ok == SUCCESS){
#ifdef DEBUG
      printf("Radio On %lu\n", call LocalTime.get());
      printfflush();
#endif
      call CollectionControl.start();
      call DisseminationControl.start();
      if (first_period_pending) {
	call BootMessage.send();
      }
    }
    else
      call RadioControl.start();
  }

  /* instead of stopping the radio directly, this method takes care of
     stopping collection and dissemination prior to stopping the
     radio.
   */
  void radioStop() {
    call DisseminationControl.stop();
    call CollectionControl.stop();
    call RadioControl.stop();
  }


  event void RadioControl.stopDone(error_t ok) { 
#ifdef DEBUG
    printf("Radio Off %lu\n", call LocalTime.get());
    printfflush();
#endif
#ifdef BLINKY
    call Leds.led1Toggle(); 
#endif
  }

  /*********** ACK Methods  *****************/
  //updates SIP models and restarts sense timers and calculate duty time
  void ackReceived(){
    uint32_t stop_time;
    uint32_t send_time;
#ifdef BLINKY
    call Leds.led2Toggle();
#endif

    call SendTimeOutTimer.stop();
    

    stop_time = call LocalTime.get();
    //Calculate the next interval
    send_time = subtract_time(stop_time, send_start_time);
    last_duty = (float) send_time;

    /* the error code has been transmitted and so can now be reset.
       The method of resetting used here allows for errors to have
       occurred between sending the message and receiving
       acknowledgement. */
    if (last_transmitted_errno < last_errno && last_transmitted_errno != 0)
      last_errno = last_errno / last_transmitted_errno;
    else
      last_errno = 1;
   
    sample_period = DEF_SENSE_PERIOD;
    

    call TransmissionControl.transmissionDone();

    restartSenseTimer();   

    /* if first time we have been acknowledged, flash the green led 3 times */
    if (! seen_first_ack) {
      seen_first_ack = TRUE;
      call BlinkStatus.setStatus(SUCCESS);
    }
  }


  /** AckValue.changed
   *
   * - triggered when ack messgaes are disseminated
   * - checks if this ack message is for the packet
   */
  event void AckValue.changed() { 
    const AckMsg *ackMsg = call AckValue.get();
    CRCStruct crs;
    uint16_t crc;
#ifdef DEBUG
    printf("ack packet rec at %lu\n", call LocalTime.get());
    printfflush();
#endif

    crs.node_id = ackMsg->node_id;
    crs.seq = ackMsg->seq;
    crc = (nx_uint16_t)call CRCCalc.crc16(&crs, sizeof crs);

#ifdef DEBUG
    printf("exp seq %u\n", expSeq);
    printf("rec seq %u\n", ackMsg->seq);
    printf("exp nid %u\n", TOS_NODE_ID);
    printf("rec nid %u\n", ackMsg->node_id);
    printf("exp CRC %u\n", crc);
    printf("rec CRC %u\n", ackMsg->crc);
    printfflush();
#endif 
    
    //check crc's, nid and seq match
    if (crc != ackMsg->crc) {
      reportError(ERR_ACK_CRC_CORRUPT);
    }
    else if (TOS_NODE_ID == ackMsg->node_id &&
	     expSeq == ackMsg->seq)
      ackReceived();
  }
  
}

