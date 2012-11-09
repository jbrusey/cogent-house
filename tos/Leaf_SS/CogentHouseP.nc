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
    interface AMSend as BNForwarder;
    interface AMSend as AckForwarder;
    interface Receive as AckReceiver;
    interface Receive as StateReceiver;
    interface Receive as BNReceiver;
    //Sensing
    interface Read<float> as ReadTemp;
    interface Read<float> as ReadHum;
    interface Read<uint16_t> as ReadPAR;
    interface Read<uint16_t> as ReadTSR;
    interface Read<float> as ReadVolt;
    interface Read<float> as ReadCO2;
    interface Read<float> as ReadVOC;
    interface Read<float> as ReadAQ;

    interface SplitControl as CurrentCostControl;
    interface Read<ccStruct *> as ReadWattage;
    interface SplitControl as HeatMeterControl;
    interface Read<hmStruct *> as ReadHeatMeter;

    //Bitmask and packstate
    interface AccessibleBitVector as Configured;
    interface BitVector as ExpectReadDone;
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
      /* UART0 must be released before the radio can work */
      if (call Configured.get(RS_POWER)) {
	packet_pending = TRUE;
	call CurrentCostControl.stop();
      }
      else {
	if (call StateSender.send(LEAF_CLUSTER_HEAD, &dataMsg, message_size) == SUCCESS) {
	  call AckTimeoutTimer.startOneShot(LEAF_TIMEOUT_TIME*1024L); // sense/send timeout
#ifdef DEBUG
	  printf("sending begun at %lu\n", call LocalTime.get());
	  printf("sending to %lu\n", LEAF_CLUSTER_HEAD);
	  printfflush();
#endif
	  sending = TRUE;
	}
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
      call Configured.set(RS_DUTY);
    }
    else if (nodeType == 1) { /* current cost */
      call Configured.set(RS_TEMPERATURE);
      call Configured.set(RS_HUMIDITY);
      call Configured.set(RS_DUTY);
      call Configured.set(RS_POWER);
      call CurrentCostControl.start();
    } 
    else if (nodeType == 2) { /* co2 */
      call Configured.set(RS_TEMPERATURE);
      call Configured.set(RS_HUMIDITY);
      call Configured.set(RS_CO2);
      call Configured.set(RS_DUTY);
    }
    else if (nodeType == 3) { /* air quality */
      call Configured.set(RS_TEMPERATURE);
      call Configured.set(RS_HUMIDITY);
      call Configured.set(RS_CO2);
      call Configured.set(RS_AQ);
      call Configured.set(RS_VOC);
      call Configured.set(RS_DUTY);
    }
    else if (nodeType == 4) { /* heat meter */
      call Configured.set(RS_HEATMETER);	  
      call Configured.set(RS_VOLTAGE);
      call HeatMeterControl.start();
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
#ifdef LEAF
      call RadioControl.start();
#endif
#ifdef CLUSTER
     sendState();
#endif
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
      phase_two_sensing = FALSE;

      // only include phase one sensing here
      for (i = 0; i < RS_SIZE; i++) { 
	if (call Configured.get(i)) {
	  call ExpectReadDone.set(i);
	  if (i == RS_TEMPERATURE)
	    call ReadTemp.read();
	  else if (i == RS_HUMIDITY)
	    call ReadHum.read();
	  else if (i == RS_PAR)
	    call ReadPAR.read();
	  else if (i == RS_TSR)
	    call ReadTSR.read();
	  else if (i == RS_VOLTAGE)
	    call ReadVolt.read();
	  else if (i == RS_POWER)
	    call ReadWattage.read();
	  else if (i == RS_HEATMETER)
	    call ReadHeatMeter.read();
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
    if (result == SUCCESS)
      call PackState.add(state_code, data);
    call ExpectReadDone.clear(raw_sensor);
    post checkDataGathered();
  }

 event void ReadTemp.readDone(error_t result, float data)
  {
    do_readDone(result, data, RS_TEMPERATURE, SC_TEMPERATURE);
  }
	
  event void ReadHum.readDone(error_t result, float data) {
    do_readDone(result, data, RS_HUMIDITY, SC_HUMIDITY);
  }
  
  event void ReadPAR.readDone(error_t result, uint16_t data) {
    do_readDone(result, data, RS_PAR, SC_PAR);
  }

  event void ReadTSR.readDone(error_t result, uint16_t data) {		
    do_readDone(result, data, RS_TSR, SC_TSR);
  }
  event void ReadCO2.readDone(error_t result, float data) {
    do_readDone(result, data, RS_CO2, SC_CO2);
  }
  event void ReadAQ.readDone(error_t result, float data) {
    do_readDone(result, data, RS_AQ, SC_AQ);
  }
  
  event void ReadVOC.readDone(error_t result, float data) {	
    do_readDone(result, data, RS_VOC, SC_VOC);
  }

  event void ReadVolt.readDone(error_t result, float data) {
    do_readDone(result,(data), RS_VOLTAGE, SC_VOLTAGE);
  }

 event void ReadHeatMeter.readDone(error_t result, hmStruct *data) {
    if (result == SUCCESS) {
      call PackState.add(SC_HEAT_ENERGY, data->energy);
      call PackState.add(SC_HEAT_VOLUME, data->volume);
    }
    call ExpectReadDone.clear(RS_HEATMETER);
    post checkDataGathered();
  }


  event void ReadWattage.readDone(error_t result, ccStruct* data) {
    if (result == SUCCESS) {
      call PackState.add(SC_POWER_MIN, data->min);
      call PackState.add(SC_POWER, data->average);
      call PackState.add(SC_POWER_MAX, data->max);
    }
    if (data->kwh > 0){
      call PackState.add(SC_POWER_KWH, data->kwh);
    }
    call ExpectReadDone.clear(RS_POWER);
    post checkDataGathered();
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
      triggered. Update any error messages.
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
    


  event void HeatMeterControl.startDone(error_t error) {}

  event void HeatMeterControl.stopDone(error_t error) {}

  event void CurrentCostControl.startDone(error_t error) {}

  event void CurrentCostControl.stopDone(error_t error) { 
    if (packet_pending) { 
      packet_pending = FALSE;
      if (call StateSender.send(LEAF_CLUSTER_HEAD, &dataMsg, message_size) == SUCCESS) {
#ifdef DEBUG
	printf("sending begun at %lu\n", call LocalTime.get());
	printfflush();
#endif
	sending = TRUE;
      }
    }
  }


  //---------------- Deal with Acknowledgements --------------------------------
  /* Receive ack message repack packet and forward to the next node in the chain 
   * if the ack packet is not for this node (deduced by hops = 0) else if the expected
   * packet has been received stop the timeout timer and restart the sense time
   */
  event message_t* AckReceiver.receive(message_t* bufPtr,void* payload, uint8_t len) {
    AckMsg *ackData;
    int h;
    int prev_hop;
    uint16_t dest;
    AckMsg* aMsg;
    
    aMsg = (AckMsg*)payload;
    if (len == sizeof(aMsg)){
      
#ifdef DEBUG
      call Leds.led2Toggle();
      printf("ack packet rec at %lu\n", call LocalTime.get());
      printfflush();
#endif    
      h=aMsg->hops;
      ackData = call AckForwarder.getPayload(&ackMsg, message_size);
      
      if (ackData != NULL) {
	if (h!=0){
	  prev_hop=(aMsg->hops)-1;
	  if (prev_hop>=0){
	    dest=aMsg->route[prev_hop];
	    ackData->hops=prev_hop;
	    ackData->seq = aMsg->seq;
	    
	    memcpy(ackData->route, aMsg->route, sizeof aMsg->route);
	    
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
	    reportError(ERR_ACK_HOP_SIZE);    
	  }
	}
	else{
	  int ackSeq = aMsg->seq;
	  
	  if (expSeq==ackSeq){
	    call AckTimeoutTimer.stop();
#ifdef LEAF
	    call RadioControl.stop();
#endif
	    //and restart timer
	    my_settings->samplePeriod = DEF_SENSE_PERIOD;
	    retries=0;
	    restartSenseTimer();
	  }
	}
      }
    } 
    else{
      reportError(ERR_PACKET_ACK_SIZE);
    }
    return bufPtr; 
  }

  event void AckForwarder.sendDone(message_t *msg, error_t ok) {
    if (ok != SUCCESS) {
      reportError(ERR_FWD_FAILED);    
    }
  }

  /* If the number of sending retries < LEAF_MAX_RETRIES then try sending the message again, else
   * assume the message is not going to get through, cancel send and call restartSenseTimer with a 
   * FAIL status, this will restart sense timer with 5 minuite period
   */
  event void AckTimeoutTimer.fired() {
    //if retries < max retries send else give up
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
#ifdef LEAF
      call RadioControl.stop();
#endif
#ifdef DEBUG
      printf("Sample Period to be used %lu\n", my_settings->samplePeriod);
      printf("ack waiting failed %lu\n", call LocalTime.get());
      printfflush();
#endif
      restartSenseTimer();
     }  
  }

  //---------------- Deal with State Message Forwarding---------------------

  //Receive a message repack and forward up to the next cluster head
  event message_t* StateReceiver.receive(message_t* bufPtr,void* payload, uint8_t len) {
    StateMsg *newData;
    int i;
    int next_hop;
    StateMsg* sMsg;
    
    sMsg = (StateMsg*)payload;

    if (len == sizeof(sMsg)){
      newData = call StateForwarder.getPayload(&fwdMsg, len);
      if (newData != NULL) { 
	next_hop=(sMsg->hops)+1;
	if (next_hop<=MAX_HOPS){
	  newData->timestamp = sMsg->timestamp;
	  newData->special = sMsg->special;
	  newData->seq = sMsg->seq;
	  newData->hops = next_hop;
	  
	  //loop through and pack the route adding this node on at the end
	  for (i = 0; i < MAX_HOPS; i++) {
	    if (i==next_hop) {
	      newData->route[i] = TOS_NODE_ID;
	    }
	    else {
	      newData->route[i]=sMsg->route[i];
	    }
	  }
	
	  memcpy(newData->packed_state_mask, sMsg->packed_state_mask,sizeof sMsg->packed_state_mask);
	  memcpy(newData->packed_state, sMsg->packed_state,sizeof sMsg->packed_state);
	  call StateForwarder.send(LEAF_CLUSTER_HEAD, &fwdMsg, len);
	}
      }
      else{
	reportError(ERR_STATE_HOP_SIZE);
      }
    }
    else{
      reportError(ERR_PACKET_STATE_SIZE);
    }

    return bufPtr;    
  }

  event void StateForwarder.sendDone(message_t *msg, error_t ok) {}


  //---------------- Deal with BN Message Forwarding---------------------

  //Receive a message repack and forward up to the next cluster head
  event message_t* BNReceiver.receive(message_t* bufPtr,void* payload, uint8_t len) {
    StateMsg *newData;
    int i;
    int next_hop;
    StateMsg* sMsg;
    
    sMsg = (StateMsg*)payload;
    if (len == sizeof(sMsg)){
      newData = call BNForwarder.getPayload(&fwdMsg, len);
      if (newData != NULL) { 
	next_hop=(sMsg->hops)+1;
	if (next_hop<=MAX_HOPS){
	  newData->timestamp = sMsg->timestamp;
	  newData->special = sMsg->special;
	  newData->seq = sMsg->seq;
	  newData->hops = next_hop;
	  
	  //loop through and pack the route adding this node on at the end
	  for (i = 0; i < MAX_HOPS; i++) {
	    if (i==next_hop) {
	      newData->route[i] = TOS_NODE_ID;
	    }
	    else {
	      newData->route[i]=sMsg->route[i];
	    }
	  }
	  
	  memcpy(newData->packed_state_mask, sMsg->packed_state_mask,sizeof sMsg->packed_state_mask);
	  memcpy(newData->packed_state, sMsg->packed_state,sizeof sMsg->packed_state);
	  call BNForwarder.send(LEAF_CLUSTER_HEAD, &fwdMsg, len);
	}
      }
      else{
	reportError(ERR_STATE_HOP_SIZE);
      }
    }
    else{
      reportError(ERR_PACKET_STATE_SIZE);
    }
    
    return bufPtr;    
  }


  event void BNForwarder.sendDone(message_t *msg, error_t ok) {}
}
