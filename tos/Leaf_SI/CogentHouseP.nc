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
    interface AMSend as StateForwarder;
    interface AMSend as AckForwarder;
    interface Receive as AckReceiver;
    interface Receive as StateReceiver;
				
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
  /* error codes should be prime. As each error occurs during a sense
     cycle, it is multiplied into last_errno. Factorising the
     resulting value gives both the number of occurences and the type.
   */
  enum {
    ERR_SEND_CANCEL_FAIL = 2,
    ERR_SEND_TIMEOUT = 3,
    ERR_SEND_FAILED = 5,
    ERR_SEND_WHILE_PACKET_PENDING = 7,
    ERR_SEND_WHILE_SENDING = 11,
    ERR_FWD_FAILED = 13,
  };

  //variables
  float last_duty = 0.;

  float last_errno = 1.;

  float last_transmitted_errno;
  
  uint32_t sense_start_time;
	
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
    int routeLen;
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
      expSeq = msgSeq;
      msgSeq++;
      newData->seq = expSeq;
      newData->timestamp = call LocalTime.get();
      newData->hops = 0;
      routeLen = sizeof(newData->route)/sizeof(uint16_t);
      for (i = 0; i < routeLen; i++) {
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
	call AckTimeoutTimer.startOneShot(LEAF_TIMEOUT_TIME*1024L); // 5 sec sense/send timeout
#ifdef DEBUG
	  printf("sending begun at %lu\n", call LocalTime.get());
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

#ifdef CLUSTER
      call RadioControl.start();
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
    else if (nodeType == 1) { /* current cost */
      call Configured.set(RS_TEMPERATURE);
      call Configured.set(RS_HUMIDITY);
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
    call SenseTimer.startOneShot(0);
  }

  /** Restart the sense timer as a one shot. Using a one shot here
      rather than periodic removes the possibility of re-entering the
      sense loop before the last one has finished. The only slight
      problem here is that this may induce a slight drift in when the
      timer fires.

      This method is called both when the send completes (sendDone)
      and when the send times out.
   */
  void restartSenseTimer(error_t result) {
    uint32_t stop_time = call LocalTime.get();
    uint32_t send_time, next_interval;
    int i =0;
    retries=0;
    sending = FALSE;
#ifdef LEAF
    call RadioControl.stop();
#endif
#ifdef DEBUG
    printf("restartSenseTimer at %lu\n", call LocalTime.get());
    printfflush();
#endif

    if (result==SUCCESS){
#ifdef DEBUG
        printf("Recieved ack updating\n");
        printfflush();
#endif
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
    }

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
#ifdef LEAF
	call RadioControl.start();
#endif
#ifdef CLUSTER
	sendState();
#endif
      }
      else {
	restartSenseTimer(FAIL);
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

    sense_start_time = call LocalTime.get();
#ifdef BLINKY
    call Leds.led0Toggle();
#endif

    if (! sending) { 
#ifdef DEBUG
      printf("sensing begun at %lu\n", sense_start_time);
      printfflush();
#endif
      call ExpectReadDone.clearAll();
      call PackState.clear();


      for (i = 0; i < RS_SIZE; i++) { 
	if (call Configured.get(i)) {
	  call ExpectReadDone.set(i);
	  if (i == RS_TEMPERATURE)
	    call ReadTemp.read();
	  else if (i == RS_HUMIDITY)
	    call ReadHum.read();
	  else if (i == RS_CO2)
	    call ReadCO2.read();
	  else if (i == RS_AQ)
	    call ReadAQ.read();
	  else if (i == RS_VOC)
	    call ReadVOC.read();
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

  void do_readDone(error_t result, float data, uint raw_sensor, uint state_code) 
  {
    if (result == SUCCESS)
      call PackState.add(state_code, data);
    call ExpectReadDone.clear(raw_sensor);
    post checkDataGathered();
  }

  void do_readDone_delta(error_t result, FilterState* s, uint raw_sensor, uint state_code, uint delta_state_code) 
  {
    if (result == SUCCESS){
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
#ifdef LEAF
	sendState();
#endif
      }
    else
      call RadioControl.start();
  }


  //Empty methods
  event void RadioControl.stopDone(error_t ok) { 
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
  //receive ack message
  event message_t* AckReceiver.receive(message_t* bufPtr,void* payload, uint8_t len) {
    AckMsg *ackData;
    int i;
    int routeLen;
    int h;
    int prev_hop;
    uint16_t dest;
    AckMsg* aMsg;
#ifdef DEBUG
    call Leds.led2Toggle();
    printf("ack packet rec at %lu\n", call LocalTime.get());
    printfflush();
#endif
    aMsg = (AckMsg*)payload;
    
    h=aMsg->hops;
    message_size = len;
    ackData = call AckForwarder.getPayload(&ackMsg, message_size);

    if (ackData != NULL) {
      if (h!=0){
	call AckTimeoutTimer.stop();
	prev_hop=(aMsg->hops)-1;
	dest=aMsg->route[prev_hop];
	ackData->hops=prev_hop;
	ackData->seq = aMsg->seq;
	routeLen = sizeof(ackData->route)/sizeof(uint16_t);
	for (i = 0; i < routeLen; i++) {
	  ackData->route[i] = aMsg->route[i];
	}

#ifdef DEBUG
	printf("Forward ACK %lu\n", call LocalTime.get());
	printf("Hops %u\n", h);
	printf("NID %u\n", TOS_NODE_ID);
	printf("Dest %u\n", dest);
	printfflush();
#endif
	call AckForwarder.send(dest, &ackMsg, message_size);
      }
      else{
	int ackSeq = aMsg->seq;

	if (expSeq==ackSeq){
	  call AckTimeoutTimer.stop();
	  //and restart timer
	  restartSenseTimer(SUCCESS);
	}
      } 
    }
    return bufPtr;    
  }

  event void AckForwarder.sendDone(message_t *msg, error_t ok) {
    if (ok != SUCCESS) {
      reportError(ERR_FWD_FAILED);    
    }
  }

  event void AckTimeoutTimer.fired() {
    if (retries < LEAF_MAX_RETRIES) {
#ifdef DEBUG
      printf("retry called at %lu\n", call LocalTime.get());
      printfflush();
#endif

      retries+=1;
      call AckTimeoutTimer.startOneShot(LEAF_TIMEOUT_TIME*1024L); // 30 sec sense/send timeout

      if (call StateSender.send(LEAF_CLUSTER_HEAD, &dataMsg, message_size) == SUCCESS) {
#ifdef DEBUG
	printf("resending begun at %lu\n", call LocalTime.get());
	printfflush();
#endif
	sending = TRUE;
      }
    }
    else{
      //not going to get through, cancel send do not update SI/BN
      reportError(ERR_SEND_TIMEOUT);
      restartSenseTimer(FAIL); //need add a param in
     }  
  }

  //---------------- Deal with State Message Forwarding---------------------
  event message_t* StateReceiver.receive(message_t* bufPtr,void* payload, uint8_t len) {
    StateMsg *newData;
    int i;
    int pslen;
    int routeLen;
    int next_hop;
    StateMsg* sMsg;
    
    sMsg = (StateMsg*)payload;
          
    message_size = len;
    newData = call StateForwarder.getPayload(&fwdMsg, message_size);
    if (newData != NULL) { 
      next_hop=(sMsg->hops)+1;
      newData->timestamp = sMsg->timestamp;
      newData->special = sMsg->special;
      newData->seq = sMsg->seq;
      newData->hops = next_hop;
      newData->route[next_hop]=TOS_NODE_ID;
      
      routeLen = sizeof(sMsg->route)/sizeof(uint16_t);
      for (i = 0; i < routeLen; i++) {
	if (i==next_hop) {
	  newData->route[i] = TOS_NODE_ID;
	}
	else {
	  newData->route[i]=sMsg->route[i];
	}
      }
	
      for (i = 0; i < sizeof sMsg->packed_state_mask; i++) { 
	newData->packed_state_mask[i] = sMsg->packed_state_mask[i];
      }
      pslen = sizeof(sMsg->packed_state)/sizeof(float);
      for (i = 0; i < pslen; i++) {
	newData->packed_state[i] = sMsg->packed_state[i];
      }
      call StateForwarder.send(LEAF_CLUSTER_HEAD, &fwdMsg, message_size);
    }
    return bufPtr;    
  }

  event void StateForwarder.sendDone(message_t *msg, error_t ok) {
  }
}
