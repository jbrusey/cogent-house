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

    //Radio + CTP
    interface SplitControl as RadioControl;
    interface Send as StateSender;
    interface StdControl as CollectionControl;
    interface CtpInfo;
    interface Packet;
    interface LowPowerListening;    

    // ack interfaces
    interface Crc as CRCCalc;
    interface StdControl as DisseminationControl;
    interface DisseminationValue<AckMsg> as AckValue;

    //Sensing
    interface Read<float> as ReadTemp;
    interface Read<float> as ReadHum;
    interface Read<uint16_t> as ReadPAR;
    interface Read<uint16_t> as ReadTSR;
    interface Read<float> as ReadBattery;
    interface Read<float> as ReadCO2;
    interface Read<float> as ReadVOC;
    interface Read<float> as ReadAQ;

    interface SplitControl as OptiControl;
    interface Read<float> as ReadOpti;

    interface SplitControl as CurrentCostControl;
    interface Read<ccStruct *> as ReadWattage;
    interface SplitControl as HeatMeterControl;
    interface Read<hmStruct *> as ReadHeatMeter;

    //Bitmask and packstate
    interface AccessibleBitVector as Configured;
    interface BitVector as ExpectReadDone;
    interface PackState;
  }
}
implementation
{
  ConfigMsg settings;
  ConfigPerType * ONE my_settings;

  uint8_t nodeType;   /* default node type is determined by top 4 bits of node_id */
  bool sending;
  bool shutdown = FALSE;
  message_t dataMsg;
  uint16_t message_size;
  uint8_t msgSeq = 0;
  uint8_t expSeq = 255;
  uint32_t sense_start_time;
  uint32_t send_start_time;  
  uint8_t missedPKT = 0;

  bool packet_pending = FALSE;
  float last_duty = 0.;
  float last_errno = 1.;
  float last_transmitted_errno;

  task void powerDown(){
    call SenseTimer.stop();
    call CollectionControl.stop();
    call DisseminationControl.stop();
    call RadioControl.stop();
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

      if (call Configured.get(RS_POWER))
	call CurrentCostControl.start();

    //Calculate the next interval
      if (stop_time < sense_start_time) // deal with overflow
	send_time = ((UINT32_MAX - sense_start_time) + stop_time + 1);
      else
	send_time = (stop_time - sense_start_time);
    
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
  }


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

    if (call Configured.get(RS_DUTY))
      packstate_add(SC_DUTY_TIME, last_duty);

    pslen = call PackState.pack(&ps);
    message_size = sizeof (StateMsg) - sizeof newData->packed_state + pslen * sizeof (float);
    newData = call StateSender.getPayload(&dataMsg, message_size);
    if (newData != NULL) { 
      //we're going do a send so pack the msg count and then increment
      newData->timestamp = call LocalTime.get();
      newData->special = 0xc7;

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

      /* UART0 must be released before the radio can work */
      if (call Configured.get(RS_POWER)) {
	packet_pending = TRUE;
	call CurrentCostControl.stop();
      }
      else {
	if (call StateSender.send(&dataMsg, message_size) == SUCCESS) {
#ifdef DEBUG
	  printf("sending begun at %lu\n", call LocalTime.get());
	  printfflush();
#endif
	  sending = TRUE;
	}
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


  bool phase_two_sensing = FALSE;  
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
	sendState();
      }
      else { /* phase one complete - start phase two */
	phase_two_sensing = TRUE;
	post phaseTwoSensing();
      }
    }
  }

  event void SendTimeOutTimer.fired() {
    //reset errors - need to avoid getting inf --Check with JB
    if (last_transmitted_errno < last_errno && last_transmitted_errno != 0.)
      last_errno = last_errno / last_transmitted_errno;
    else
      last_errno = 1.;

    reportError(ERR_NO_ACK);
    my_settings->samplePeriod = DEF_BACKOFF_SENSE_PERIOD;

    //if packet not through after 3 times get through recompute routes
    if (missedPKT >= 2){
      call CtpInfo.recomputeRoutes();
      missedPKT = 0;
    }
    else
      missedPKT += 1;

#ifdef DEBUG
    printf("ack receving failed %lu\n", call LocalTime.get());
    printf("Sample Period to be used %lu\n", my_settings->samplePeriod);
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
    call RadioControl.start();

    nodeType = TOS_NODE_ID >> 12;
    my_settings = &settings.byType[nodeType];
    my_settings->samplePeriod = DEF_SENSE_PERIOD;
    my_settings->blink = FALSE;

    call Configured.clearAll();
    if (nodeType == 1) { 
      call Configured.set(RS_TEMPERATURE);
      call Configured.set(RS_HUMIDITY);
      call Configured.set(RS_DUTY);
      call Configured.set(RS_POWER);
      //powered so set to always be awake
      call LowPowerListening.setLocalWakeupInterval(0); //probably not needed
    }
    
    call BlinkTimer.startOneShot(512L); /* start blinking to show that we are up and running */

    sending = FALSE;
    call SenseTimer.startOneShot(DEF_FIRST_PERIOD);
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
      if (last_errno != 1.)
	packstate_add(SC_ERRNO, last_errno);
      last_transmitted_errno = last_errno;

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
	    call ReadBattery.read();
	  else if (i == RS_POWER)
	    call ReadWattage.read();
	  else if (i == RS_OPTI)
	    call ReadOpti.read();
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


  /*********** Sensing Methods *****************/  

  void do_readDone(error_t result, float data, uint raw_sensor, uint state_code){
    if (result == SUCCESS)
      packstate_add(state_code, data);
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

  event void ReadBattery.readDone(error_t result, float data) {	
    do_readDone(result, data, RS_VOLTAGE, SC_VOLTAGE);
    if (data < LOW_VOLTAGE)
      post powerDown();
  }
  
 event void ReadHeatMeter.readDone(error_t result, hmStruct *data) {
    if (result == SUCCESS) {
      call PackState.add(SC_HEAT_ENERGY, data->energy);
      call PackState.add(SC_HEAT_VOLUME, data->volume);
    }
    call ExpectReadDone.clear(RS_HEATMETER);
    post checkDataGathered();
  }

  event void ReadOpti.readDone(error_t result, float data) {
    //
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

  /*********** Radio Control *****************/

  event void RadioControl.startDone(error_t ok) {
    if (ok == SUCCESS){
      call CollectionControl.start();
      call DisseminationControl.start();
#ifdef DEBUG
      printf("Radio On %lu\n", call LocalTime.get());
      printfflush();
#endif

      if (call Configured.get(RS_POWER))
	call CurrentCostControl.start();

    }
    else
      call RadioControl.start();
  }

  event void RadioControl.stopDone(error_t ok) { 
    call DisseminationControl.stop();
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
    if (stop_time < send_start_time) // deal with overflow
      send_time = ((UINT32_MAX - send_start_time) + stop_time + 1);
    else
      send_time = (stop_time - send_start_time);
    last_duty = (float) send_time;
    
    my_settings->samplePeriod = DEF_SENSE_PERIOD;
    
    restartSenseTimer();   
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
    if (crc == ackMsg->crc)
      if (TOS_NODE_ID == ackMsg->node_id)
	if (expSeq == ackMsg->seq){
    	  ackReceived();
    	}
    return;
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

  event void CurrentCostControl.startDone(error_t error) {
#ifdef DEBUG
    printf("Current cost start at %lu\n", call LocalTime.get());
    printfflush();
#endif
  }

  event void CurrentCostControl.stopDone(error_t error) { 
#ifdef DEBUG
    printf("Current cost stop at %lu\n", call LocalTime.get());
    printfflush();
#endif

    if (packet_pending) { 
      packet_pending = FALSE;
      if (call StateSender.send(&dataMsg, message_size) == SUCCESS) {
	sending = TRUE;
      }
    }
      
  }

  event void OptiControl.startDone(error_t error) { }
 
  event void OptiControl.stopDone(error_t error) {}  
  
}

