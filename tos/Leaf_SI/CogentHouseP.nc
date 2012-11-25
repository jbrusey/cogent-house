// -*- c -*-

module CogentHouseP
{
  uses {
    //low-level stuff
    interface Timer<TMilli> as SenseTimer;
    interface Timer<TMilli> as AckTimeoutTimer;
    interface Timer<TMilli> as BlinkTimer;
    interface Leds;
    interface Boot;
    
    //radio
    interface SplitControl as RadioControl;
    interface AMSend as StateSender;
    interface Receive as AckReceiver;
    //SI Sensing
    interface Read<FilterState *> as ReadTemp;
    interface TransmissionControl as TempTrans;
    interface Read<FilterState *> as ReadHum;
    interface TransmissionControl as HumTrans;
    interface Read<FilterState *> as ReadVolt;
    interface TransmissionControl as VoltTrans;
    interface Read<FilterState *> as ReadCO2;
    interface TransmissionControl as CO2Trans;
    interface Read<FilterState *> as ReadAQ;
    interface TransmissionControl as AQTrans;
    interface Read<FilterState *> as ReadVOC;
    interface TransmissionControl as VOCTrans;

    //Bitmask and packstate
    interface AccessibleBitVector as Configured;
    interface BitVector as ExpectReadDone;
    interface BitVector as ExpectSendDone;
    interface PackState;

    //Time
    interface LocalTime<TMilli>;
  }
}
implementation
{
  float last_duty = 0.;

  float last_errno = 1.;

  float last_transmitted_errno;
  
  uint32_t sense_start_time;
  bool phase_two_sensing = FALSE;
	
  ConfigMsg settings;
  ConfigPerType * ONE my_settings;

  /* default node type is determined by top 4 bits of node_id */
  uint8_t nodeType;

  bool sending;

  bool packet_pending = FALSE;

  message_t dataMsg;
  message_t fwdMsg;
  message_t ackMsg;
  uint16_t message_size;
  uint8_t msgSeq = 0;
  uint8_t retries = 0;
  uint8_t expSeq = 0;

  int periodsToHeartbeat=HEARTBEAT_PERIOD;
  struct nodeType nt;
	

  /** reportError records a code to be sent on the next transmission. 
   * @param errno error code
   */
  void reportError(uint8_t errno) {
#ifdef DEBUG
    printf("Error message: %u\n", errno);
    printfflush();
#endif
    last_errno *= errno;
  }


  ////////////////////////////////////////////////////////////
  //sending methods


  void sendState()
  {
    packed_state_t ps;
    StateMsg *newData;
    int pslen;
    int i;
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

    //increment and pack seq
    expSeq = msgSeq;
    msgSeq++;
    call PackState.add(SC_SEQ, expSeq);

    if (periodsToHeartbeat<=0)
      call PackState.add(SC_HEARTBEAT, 1);

    if (call Configured.get(RS_DUTY))
      call PackState.add(SC_DUTY_TIME, last_duty);
    if (last_errno != 1.)
      call PackState.add(SC_ERRNO, last_errno);

    last_transmitted_errno = last_errno;
    pslen = call PackState.pack(&ps);
		
    message_size = sizeof (StateMsg) - (SC_SIZE - pslen) * sizeof (float);
    newData = call StateSender.getPayload(&dataMsg, message_size);
    if (newData != NULL) { 
      newData->special = 0xc7;
      //we're going do a send so pack the msg count and then increment
      newData->timestamp = call LocalTime.get();
      newData->hops = 0;

      //pack empty route array
      for (i = 0; i < MAX_HOPS; i++) {
	if (i==0) {
          newData->route[i] = TOS_NODE_ID;
        }
	else {
          newData->route[i]=0;
        }
      }
     
      for (i = 0; i < sizeof newData->packed_state_mask; i++) { 
	newData->packed_state_mask[i] = ps.mask[i];
      }
      for (i = 0; i < pslen; i++) {
	newData->packed_state[i] = ps.p[i];
      }
      if (call StateSender.send(LEAF_CLUSTER_HEAD, &dataMsg, message_size) == SUCCESS) {
	call AckTimeoutTimer.startOneShot(LEAF_TIMEOUT_TIME); 
#ifdef DEBUG
	  printf("sending begun at %lu\n", call LocalTime.get());
	  printf("sending to %lu\n", LEAF_CLUSTER_HEAD);
	  printfflush();
#endif
	sending = TRUE;
      }
    }
  }	
  
  ////////////////////////////////////////////////////////////
	
  event void Boot.booted() {
    // initial config
#ifdef DEBUG
    printf("Booted %lu\n", call LocalTime.get());
    printfflush();
#endif

    nodeType = TOS_NODE_ID >> 12;
    my_settings = &settings.byType[nodeType];
    my_settings->samplePeriod = DEF_SENSE_PERIOD;
    my_settings->blink = FALSE;
		
    call Configured.clearAll();
    if (nodeType == 0) { 
      call Configured.set(RS_TEMPERATURE);
      call Configured.set(RS_HUMIDITY);
      call Configured.set(RS_VOLTAGE);
    }
    else if (nodeType == 2) { /* co2 */
      call Configured.set(RS_TEMPERATURE);
      call Configured.set(RS_HUMIDITY);
      call Configured.set(RS_CO2);
    }
    else if (nodeType == 3) { /* air quality */
      call Configured.set(RS_TEMPERATURE);
      call Configured.set(RS_HUMIDITY);
      call Configured.set(RS_CO2);
      call Configured.set(RS_AQ);
      call Configured.set(RS_VOC);
    }
    
    call BlinkTimer.startOneShot(512L); /* start blinking to show that we are up and running */

    sending = FALSE;
    call SenseTimer.startOneShot(DEF_FIRST_PERIOD);
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
    sending = FALSE;

#ifdef DEBUG
    printf("restartSenseTimer at %lu\n", call LocalTime.get());
    printfflush();
#endif

    //Calculate the next interval
    if (stop_time < sense_start_time) // deal with overflow
      send_time = ((UINT32_MAX - sense_start_time) + stop_time + 1);
    else
      send_time = (stop_time - sense_start_time);
    last_duty = (float) send_time;
    
    if (my_settings->samplePeriod < send_time)
      next_interval = 0;
    else
      next_interval = my_settings->samplePeriod - send_time;

#ifdef DEBUG
    printf("startOneShot at %lu\n", call LocalTime.get());
    printf("interval of %lu\n", next_interval);
    printfflush();
#endif
    call SenseTimer.startOneShot(next_interval);

    if (my_settings->blink)
      call Leds.led1Off();
  }

  task void phaseTwoSensing();

  /* checkDataGathered
   * - only transmit data once all sensors have been read
   */
  task void checkDataGathered() {
    bool allDone = TRUE;
    bool toSend = FALSE;
    uint8_t i;

    for (i = 0; i < RS_SIZE; i++) {
      if (call ExpectReadDone.get(i)) {
	allDone = FALSE;
	break;
      }
    }

    if (allDone) {
      if (phase_two_sensing) {
#ifdef DEBUG
	printf("allDone %lu\n", call LocalTime.get());
	printfflush();
#endif
	
	for (i = 0; i < RS_SIZE; i++) {
	  if (call ExpectSendDone.get(i)) {
	    toSend = TRUE;
	    break;
	  }
	}

	if (toSend){
	  call RadioControl.start();
	}
	else
	  restartSenseTimer();
      }
      else { /* phase one complete - start phase two */
	phase_two_sensing = TRUE;
	post phaseTwoSensing();
      }
    }
  }

  /* SenseTimer.fired
   *
   * - begin sensing cycle by requesting, in parallel, for all active
       sensors to start reading.
  */
  event void SenseTimer.fired() {
    int i;

    //starting reads decrease periods To Heartbeat
    periodsToHeartbeat=periodsToHeartbeat-1;

    sense_start_time = call LocalTime.get();
#ifdef BLINKY
    call Leds.led0Toggle();
#endif

    if (! sending) { 
#ifdef DEBUG
      printf("\n\nsensing begun at %lu\n", sense_start_time);
      printf("periodsToHeartbeat %u\n", periodsToHeartbeat);
      printfflush();
#endif
      call ExpectReadDone.clearAll();
      call PackState.clear();
      phase_two_sensing = FALSE;

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

  /* perform any phase two sensing */
  task void phaseTwoSensing() {
    int i;
    for (i = 0; i < RS_SIZE; i++) { 
      if (call Configured.get(i)) {
	call ExpectReadDone.set(i);
	if (i == RS_CO2)
	  call ReadCO2.read();
	else if (i == RS_AQ)
	  call ReadAQ.read();
	else if (i == RS_VOC)
	  call ReadVOC.read();
	else
	  call ExpectReadDone.clear(i);
      }
    }
    post checkDataGathered();
  }


  void do_readDone(error_t result, float data, uint raw_sensor, uint state_code) 
  {
    if (result == SUCCESS || periodsToHeartbeat<=0)
      call PackState.add(state_code, data);
    call ExpectReadDone.clear(raw_sensor);
    post checkDataGathered();
  }

  void do_readDone_delta(error_t result, FilterState* s, uint raw_sensor, uint state_code, uint delta_state_code) 
  {
    if (result == SUCCESS || periodsToHeartbeat<=0){

      call PackState.add(state_code, s->x);
      call PackState.add(delta_state_code, s->dx);
      call ExpectSendDone.set(raw_sensor);
    }
    call ExpectReadDone.clear(raw_sensor);
    post checkDataGathered();
  }

  event void ReadTemp.readDone(error_t result, FilterState* data){
    do_readDone_delta(result, data, RS_TEMPERATURE, SC_TEMPERATURE, SC_D_TEMPERATURE);
  }
	
  event void ReadHum.readDone(error_t result, FilterState* data) {
    do_readDone_delta(result, data, RS_HUMIDITY, SC_HUMIDITY, SC_D_HUMIDITY);
  }    

  event void ReadCO2.readDone(error_t result, FilterState* data) {
    do_readDone_delta(result, data, RS_CO2, SC_CO2, SC_D_CO2);
 }
    
  event void ReadAQ.readDone(error_t result, FilterState* data) {
    do_readDone_delta(result, data, RS_AQ, SC_AQ, SC_D_AQ);
  }
 event void ReadVOC.readDone(error_t result, FilterState* data) {
    do_readDone_delta(result, data, RS_VOC, SC_VOC, SC_D_VOC);
  }

  event void ReadVolt.readDone(error_t result, FilterState* data) {
    do_readDone_delta(result, data, RS_VOLTAGE, SC_VOLTAGE, SC_D_VOLTAGE);
  }

  event void RadioControl.startDone(error_t ok) {
    if (ok == SUCCESS)
      {
#ifdef DEBUG
        printf("Radio On\n");
        printfflush();
#endif
	sendState();
      }
    else
      call RadioControl.start();
  }


  //Empty methods
  event void RadioControl.stopDone(error_t ok) { 
#ifdef DEBUG
        printf("Radio Off\n");
        printfflush();
#endif

#ifdef BLINKY
    call Leds.led1Toggle(); 
#endif
  }



  /** When a message has been successfully transmitted, this event is
      triggered. At this point, we stop the timeout timer, restart the
      sense timer and restart the current-cost if it is needed.
  */
  event void StateSender.sendDone(message_t *msg, error_t ok) {
    if (ok != SUCCESS) {
#ifdef BLINKY
      call Leds.led0Toggle(); 
#endif
      reportError(ERR_SEND_FAILED);    
    }
    else {
      if (last_transmitted_errno < last_errno && last_transmitted_errno != 0.)
	last_errno = last_errno / last_transmitted_errno;
      else
	last_errno = 1.;
    }
  }


  ////////////////////////////////////////////////////////////
  // Produce a nice pattern on start-up
  //
  uint8_t blink_state = 0;

  uint8_t gray[] = { 0, 1, 3, 2, 6, 7, 5, 4 };

  event void BlinkTimer.fired() { 
    if (blink_state >= 60) { /* 30 seconds */
      call Leds.set(0);
    }
    else { 
      blink_state++;
      call BlinkTimer.startOneShot(512L);
      call Leds.set(gray[blink_state % (sizeof gray / sizeof gray[0])]);
    }
  }


  //---------------- Deal with Acknowledgements --------------------------------
  event message_t* AckReceiver.receive(message_t* msg,void* payload, uint8_t len) {
    int h;
    AckMsg* aMsg;
    int i;

#ifdef DEBUG
    call Leds.led2Toggle();
    printf("ack packet rec at %lu\n", call LocalTime.get());
    printfflush();
#endif
    aMsg = (AckMsg*)payload;
    if (len == sizeof(AckMsg)){
      h=aMsg->hops;
      
#ifdef DEBUG
      call Leds.led2Toggle();
      printf("hops %u\n", h);
      printfflush();
#endif   
      
      if (h==0){
	int ackSeq = aMsg->seq;	 
	
#ifdef DEBUG
	call Leds.led2Toggle();
	printf("exp seq %u\n", expSeq);
	printf("rec seq %u\n", ackSeq);
	printfflush();
#endif 
	if (expSeq==ackSeq){
	  
#ifdef DEBUG
	  call Leds.led2Toggle();
	  printf("correct packet confirtmed at %lu\n", call LocalTime.get());
	  printfflush();
#endif   
	  
	  call AckTimeoutTimer.stop();
	  call RadioControl.stop();
	  
	  my_settings->samplePeriod = DEF_SENSE_PERIOD;
	  retries=0;
	  //update txcontrol
	  for (i = 0; i < RS_SIZE; i ++) {
	    if (call ExpectSendDone.get(i))
	      switch (i) {
	      case RS_TEMPERATURE:
		call TempTrans.transmissionDone();
		break;
	      case RS_HUMIDITY:
		call HumTrans.transmissionDone();
		break;
	      case RS_VOLTAGE:
		call VoltTrans.transmissionDone();
		break;
	      case RS_CO2:
		call CO2Trans.transmissionDone();
		break;
	      default:
		break;
	      }
	  }
	  call ExpectSendDone.clearAll();

	  //reset heartbeat period
	  periodsToHeartbeat=HEARTBEAT_PERIOD;

	  restartSenseTimer();
	}
      }
    }
    else{
      reportError(ERR_PACKET_ACK_SIZE);
    }
    return msg; 
  }


  /* If the number of sending retries < LEAF_MAX_RETRIES then try sending the message again, else
   * assume the message is not going to get through, cancel send and call restartSenseTimer with a 
   * FAIL status, this will restart sense timer with 5 minuite period
   */
  event void AckTimeoutTimer.fired() {
    //if retries < max retries send else give up

#ifdef DEBUG
      printf("timeout at %lu\n", call LocalTime.get());
      printfflush();
#endif
    if (retries < LEAF_MAX_RETRIES) {
      retries+=1;
      call AckTimeoutTimer.startOneShot(LEAF_TIMEOUT_TIME);
      if (call StateSender.send(LEAF_CLUSTER_HEAD, &dataMsg, message_size) == SUCCESS) {
	sending = TRUE;
      }
#ifdef DEBUG
      printf("resending begun at %lu\n", call LocalTime.get());
      printfflush();
#endif
    }
    else{
      reportError(ERR_SEND_TIMEOUT);
      my_settings->samplePeriod = DEF_BACKOFF_SENSE_PERIOD;
      retries=0;
      call RadioControl.stop();

#ifdef DEBUG
      printf("Sample Period to be used %lu\n", my_settings->samplePeriod);
      printf("ack waiting failed %lu\n", call LocalTime.get());
      printfflush();
#endif
      restartSenseTimer();
    }  
  }
  
}
