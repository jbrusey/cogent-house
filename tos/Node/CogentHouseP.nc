// -*- c -*-
module CogentHouseP
{
  uses {
    //Basic Interfaces
    interface Boot;
    interface Leds;
    interface LocalTime<TMilli>;

    //Timers
    interface Timer<TMilli> as SenseTimer;
    interface Timer<TMilli> as BlinkTimer;
    interface Timer<TMilli> as SendTimeOutTimer;
    interface Timer<TMilli> as BootSendTimeOutTimer;

    //Radio + CTP
    interface SplitControl as RadioControl;
    interface Send as StateSender;
    interface Send as BootSender;
    interface StdControl as CollectionControl;
    interface CtpInfo;
    interface Packet;
    interface LowPowerListening;    

    // ack interfaces
    interface Crc as CRCCalc;
    interface StdControl as DisseminationControl;
    interface DisseminationValue<AckMsg> as AckValue;

    //SIP Modules
    interface SIPController<FilterState *> as ReadTemp;
    interface SIPController<FilterState *> as ReadHum;
    interface SIPController<FilterState *> as ReadVolt;
    interface TransmissionControl;
       
    //Bitmask and packstate
    interface AccessibleBitVector as Configured;
    interface BitVector as ExpectReadDone;
    interface PackState;
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

/********* Boot Message Methods **********/
  /** sendBoot - at boot time, send an initial packet (without
      checking for ack) that specifies the current version 
   */
  void sendBoot()
  {
    BootMsg *newData;
    
#ifdef DEBUG
    printf("sendBoot %lu\n", call LocalTime.get());
    printfflush();
#endif

    message_size = sizeof (BootMsg);
    newData = call BootSender.getPayload(&dataMsg, message_size);
    if (newData != NULL) { 
      newData->special = SPECIAL;

      memcpy(newData->version, DEF_HG_REVISION, sizeof(newData->version) - 1);

      call BootSendTimeOutTimer.startOneShot(BOOT_TIMEOUT_TIME);
      if (call BootSender.send(&dataMsg, message_size) == SUCCESS) {
#ifdef DEBUG
	  printf("boot sending begun at %lu\n", call LocalTime.get());
	  printfflush();
#endif
      }
    }
  }

  /** startFirstSensing starts the sense timer after the boot message
      has been sent (or timed-out) */
  void startFirstSensing()
  {
    call SenseTimer.startOneShot(DEF_FIRST_PERIOD);
    first_period_pending = FALSE;
  }

  /** BootSender.sendDone - sending of boot message has completed so
      now we can start normal sensing.
   */
  event void BootSender.sendDone(message_t *msg, error_t ok) {
#ifdef DEBUG
    printf("Boot sending done at %lu ok=%u\n", call LocalTime.get(), ok);
    printfflush();
#endif
    if (ok == SUCCESS) { 
      call BootSendTimeOutTimer.stop();
      startFirstSensing();
    }
  }

  /** BootSendTimeOutTimer.fired - if the boot send message times out, cancel it
   */
  event void BootSendTimeOutTimer.fired() {
    call BootSender.cancel(&dataMsg);
    /* don't retry - just get on with the next sensing round */
    startFirstSensing();
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


  /* checkDataGathered
   * - only transmit data once all sensors have been read
   */
  task void checkDataGathered() {
    bool allDone = TRUE;
    uint8_t i;

    for (i = 0; i < RS_SIZE; i++) {
      if (call ExpectReadDone.get(i)) {
	allDone = FALSE;
	break;
      }
    }

    if (allDone) {
#ifdef DEBUG
      printf("allDone %lu\n", call LocalTime.get());
      printfflush();
#endif
	
      if (call TransmissionControl.hasEvent()) {
	  sendState();
      }
      else
	restartSenseTimer();

    }
  }

  event void SendTimeOutTimer.fired() {
    sample_period = DEF_BACKOFF_SENSE_PERIOD;

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
    
    call BlinkTimer.startOneShot(512L); /* start blinking to show that we are up and running */

    //Inititalise filters -- Configured in the makefile
    call ReadTemp.init(SIP_TEMP_THRESH, SIP_TEMP_MASK, SIP_TEMP_ALPHA, SIP_TEMP_BETA);
    call ReadHum.init(SIP_HUM_THRESH, SIP_HUM_MASK, SIP_HUM_ALPHA, SIP_HUM_BETA);
    call ReadVolt.init(SIP_BATTERY_THRESH, SIP_BATTERY_MASK, SIP_BATTERY_ALPHA, SIP_BATTERY_BETA);

    nodeType = TOS_NODE_ID >> 12;
    sample_period = DEF_SENSE_PERIOD;

    // Configure the node for attached sensors.

    call Configured.clearAll();
    call Configured.set(RS_TEMPERATURE);
    call Configured.set(RS_HUMIDITY);
    call Configured.set(RS_VOLTAGE);

    sending = FALSE;

    first_period_pending = TRUE;
    call RadioControl.start();
  }

  /* SenseTimer.fired
   *
   * - begin sensing cycle by requesting, in parallel, for all active
   * sensors to start reading.
   */
  event void SenseTimer.fired() {
    int i;
#ifdef BLINKY
    call Leds.led0Toggle();
#endif
    sense_start_time = call LocalTime.get();
    if (! sending) { 
#ifdef DEBUG
      printf("\n\nsensing begun at %lu\n", sense_start_time);
      printfflush();
#endif
      call ExpectReadDone.clearAll();
      call PackState.clear();
      if (last_errno != 1)
	packstate_add(SC_ERRNO, (float) last_errno);
      last_transmitted_errno = last_errno;

      // only include phase one sensing here
      for (i = 0; i < RS_SIZE; i++) { 
	if (call Configured.get(i)) {
	  call ExpectReadDone.set(i);
	  if (i == RS_TEMPERATURE)
	    call ReadTemp.read();
	  else if (i == RS_HUMIDITY)
	    call ReadHum.read();
	  else if (i == RS_VOLTAGE)
	    call ReadVolt.read();
	  else
	    call ExpectReadDone.clear(i);
	}
      }
      /* it could be that no sensors are active but we still need to
	 send a packet (e.g. for duty cycle info)
      */
      post checkDataGathered();

    }
  }

  /* /\* perform any phase two sensing *\/ */
  /* task void phaseTwoSensing() { */
  /*   int i; */
  /*   for (i = 0; i < RS_SIZE; i++) {  */
  /*     if (call Configured.get(i)) { */
  /* 	call ExpectReadDone.set(i); */
  /* 	/\* do any two phase sensing here *\/ */
  /* 	call ExpectReadDone.clear(i); */
  /*     } */
  /*   } */
  /*   post checkDataGathered(); */
  /* } */


  /*********** Sensing Methods *****************/  

  void do_readDone(error_t result, float data, uint raw_sensor, uint state_code){
    if (result == SUCCESS)
      packstate_add(state_code, data);
    call ExpectReadDone.clear(raw_sensor);
    post checkDataGathered();
  }

  void do_readDone_pass(error_t result, FilterState* s, uint raw_sensor, uint state_code) 
  {
    if (call ExpectReadDone.get(raw_sensor)) {
      if (result == SUCCESS)
	packstate_add(state_code, s->x);
      call ExpectReadDone.clear(raw_sensor);
      post checkDataGathered();
    }
  }

  void do_readDone_filterstate(error_t result, FilterState* s, uint raw_sensor, uint state_code, uint delta_state_code) 
  {
    if (call ExpectReadDone.get(raw_sensor)) { 
      if (result == SUCCESS){
	packstate_add(state_code, s->x);
	packstate_add(delta_state_code, s->dx);
      }
      call ExpectReadDone.clear(raw_sensor);
      post checkDataGathered();
    }
  }

  event void ReadTemp.readDone(error_t result, FilterState* data){
    do_readDone_filterstate(result, data, RS_TEMPERATURE, SC_TEMPERATURE, SC_D_TEMPERATURE);
  }

  event void ReadHum.readDone(error_t result, FilterState* data){
    do_readDone_filterstate(result, data, RS_HUMIDITY, SC_HUMIDITY, SC_D_HUMIDITY);
  }

  event void ReadVolt.readDone(error_t result, FilterState* data){
    do_readDone_filterstate(result, data, RS_VOLTAGE, SC_VOLTAGE, SC_D_VOLTAGE);
    if (result == SUCCESS && data->x < LOW_VOLTAGE)
      post powerDown();
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
	sendBoot();
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


  

  ////////////////////////////////////////////////////////////
  // Produce a nice pattern on start-up
  //
  uint8_t blink_state = 0;
  uint8_t blink_thrice_state = 0;

  uint8_t gray[] = { 0, 1, 3, 2, 6, 7, 5, 4 };

  void blinkThrice(bool ok) {
    if (blink_thrice_state < 6) {
      blink_thrice_state++;
      call BlinkTimer.startOneShot(1024L);
      if (blink_thrice_state == 1) 
	call Leds.set(0);
      else if (ok)
	call Leds.led1Toggle(); /* green */
      else
	call Leds.led0Toggle(); /* red */
    }
    else 
      call Leds.set(0);
  }

  event void BlinkTimer.fired() { 
    if (seen_first_ack)
      blinkThrice(TRUE);
    else if (blink_state >= 2 * BLINK_SECONDS) { /* 60 seconds */
      blinkThrice(FALSE);
    }
    else { 
      blink_state++;
      call BlinkTimer.startOneShot(512L);
      call Leds.set(gray[blink_state % (sizeof gray / sizeof gray[0])]);
    }
  }
  

  
}

