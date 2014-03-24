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

#ifndef BN
    //SIP Modules
    interface SIPController<FilterState *> as ReadTemp;
    interface SIPController<FilterState *> as ReadHum;
    interface SIPController<FilterState *> as ReadVolt;
    interface SIPController<FilterState *> as ReadCC;
    interface SIPController<FilterState *> as ReadCO2;
    interface SIPController<FilterState *> as ReadBB;
    interface SIPController<FilterState *> as ReadVOC;
    interface SIPController<FilterState *> as ReadAQ;
    interface SIPController<FilterState *> as ReadOpti;
    interface SIPController<FilterState *> as ReadGas;
    interface SIPController<FilterState *> as ReadHMEnergy;
    interface SIPController<FilterState *> as ReadHMVolume;
    interface SIPController<FilterState *> as ReadWindow;
    interface SIPController<FilterState *> as ReadTempADC1;
    interface TransmissionControl;
    interface StdControl as OptiControl;
    interface StdControl as GasControl;
    interface SplitControl as CurrentCostControl;
    interface StdControl as HMEnergyControl;
    interface StdControl as HMVolumeControl;
#endif

#ifdef BN
    interface Heartbeat;
    interface BNController<float *> as ReadTemp;
    interface BNController<float *> as ReadHum;
    interface BNController<float> as ReadVolt;
    interface BNController<float *> as ReadCO2;
    interface BNController<float *> as ReadVOC;
    interface BNController<float *> as ReadAQ;
#endif
   
#ifndef MISSING_AC_SENSOR
    interface Read<bool> as ReadAC;
    interface SplitControl as ACControl;
#endif
    
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
  bool leafMode = FALSE;
  bool seen_first_ack = FALSE;
  message_t dataMsg;
  uint16_t message_size;
  uint8_t msgSeq = 0;
  uint8_t expSeq = 255;
  uint32_t sense_start_time;
  uint32_t send_start_time;  
  uint8_t missedPKT = 0;

  bool packet_pending = FALSE;
  float last_duty = 0.;
  uint32_t last_errno = 1;
  uint32_t last_transmitted_errno;

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


#ifndef BN
      if (call Configured.get(RS_POWER)){
        call CurrentCostControl.start();
      }
#endif


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
#ifndef BN
      if (call Configured.get(RS_POWER)) {
	packet_pending = TRUE;
	call CurrentCostControl.stop();
      }
      else {
#endif
        if (call StateSender.send(&dataMsg, message_size) == SUCCESS) {
#ifdef DEBUG
	  printf("sending begun at %lu\n", call LocalTime.get());
	  printfflush();
#endif
	  sending = TRUE;
        }
#ifndef BN
      }
#endif
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
    error_t radio_status;
#ifdef BN
    bool toSend = FALSE;
#endif
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
	
#ifndef BN
    	if (call TransmissionControl.hasEvent()){
          if (!CLUSTER_HEAD || leafMode){
	    radio_status = call RadioControl.start();
	    if (radio_status == EALREADY)
	      sendState();
	  }
	  else
	    sendState();
	}
	else
	  restartSenseTimer();
#endif

#ifdef BN
	// only include phase one sensing here
	for (i = 0; i < RS_SIZE; i++) { 
	  if (call Configured.get(i)) {
	    if (i == RS_TEMPERATURE)
	      toSend = call ReadTemp.hasEvent();
	    else if (i == RS_HUMIDITY)
	      toSend = call ReadHum.hasEvent();
	    else if (i == RS_VOLTAGE)
	      toSend = call ReadVolt.hasEvent();
	    else if (i == RS_CO2)
	      toSend = call ReadCO2.hasEvent();
	    else if (i == RS_AQ)
	      toSend = call ReadAQ.hasEvent();
	    else if (i == RS_VOC)
	      toSend = call ReadVOC.hasEvent();
	    else
	      continue;
	    if (toSend)
	      break;
	  }
	}
	if  (toSend || call Heartbeat.triggered()){
          if (!CLUSTER_HEAD || leafMode){
	    radio_status = call RadioControl.start();
	    if (radio_status == EALREADY)
	      sendState();
	  }
	  else
	    sendState();
	}
	else
	  restartSenseTimer();
#endif

      }
      else { /* phase one complete - start phase two */
	phase_two_sensing = TRUE;
	post phaseTwoSensing();
      }
    }
  }

  event void SendTimeOutTimer.fired() {
    reportError(ERR_NO_ACK);
    my_settings->samplePeriod = DEF_BACKOFF_SENSE_PERIOD;

    //if packet not through after 3 times get through recompute routes
    if (missedPKT >= 5){
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
    if (!CLUSTER_HEAD || leafMode)
      call RadioControl.stop();
    restartSenseTimer();
  }


  /********* Main Loop Methods **********/
  
  event void Boot.booted(){
#ifdef DEBUG
    printf("Booted %lu\n", call LocalTime.get());
    printfflush();
#endif
    
    call BlinkTimer.startOneShot(512L); /* start blinking to show that we are up and running */

#ifdef BN
    call Heartbeat.init();
#endif

#ifndef BN
    //Inititalise filters -- Configured in the makefile
    call ReadTemp.init(SIP_TEMP_THRESH, SIP_TEMP_MASK, SIP_TEMP_ALPHA, SIP_TEMP_BETA);
    call ReadHum.init(SIP_HUM_THRESH, SIP_HUM_MASK, SIP_HUM_ALPHA, SIP_HUM_BETA);
    call ReadVolt.init(SIP_BATTERY_THRESH, SIP_BATTERY_MASK, SIP_BATTERY_ALPHA, SIP_BATTERY_BETA);
    call ReadCO2.init(SIP_CO2_THRESH, SIP_CO2_MASK, SIP_CO2_ALPHA, SIP_CO2_BETA);
    call ReadBB.init(SIP_BB_THRESH, SIP_BB_MASK, SIP_BB_ALPHA, SIP_BB_BETA);
    call ReadVOC.init(SIP_VOC_THRESH, SIP_VOC_MASK, SIP_VOC_ALPHA, SIP_VOC_BETA);
    call ReadAQ.init(SIP_AQ_THRESH, SIP_AQ_MASK, SIP_AQ_ALPHA, SIP_AQ_BETA);
    call ReadOpti.init(SIP_OPTI_THRESH, SIP_OPTI_MASK, SIP_OPTI_ALPHA, SIP_OPTI_BETA);
    call ReadGas.init(SIP_GAS_THRESH, SIP_GAS_MASK, SIP_GAS_ALPHA, SIP_GAS_BETA);
    call ReadHMEnergy.init(SIP_HME_THRESH, SIP_HME_MASK, SIP_HME_ALPHA, SIP_HME_BETA);
    call ReadHMVolume.init(SIP_HMV_THRESH, SIP_HMV_MASK, SIP_HMV_ALPHA, SIP_HMV_BETA);
    call ReadWindow.init(SIP_WINDOW_THRESH, SIP_WINDOW_MASK, SIP_WINDOW_ALPHA, SIP_WINDOW_BETA);
    call ReadCC.init(SIP_CC_THRESH, SIP_CC_MASK, SIP_CC_ALPHA, SIP_CC_BETA);
    call ReadTempADC1.init(SIP_TEMPADC_THRESH, SIP_TEMPADC_MASK, SIP_TEMPADC_ALPHA, SIP_TEMPADC_BETA);
#endif

    nodeType = TOS_NODE_ID >> 12;
    my_settings = &settings.byType[nodeType];
    my_settings->samplePeriod = DEF_SENSE_PERIOD;
    my_settings->blink = FALSE;

    // Configure the node for attached sensors.

    call Configured.clearAll();
    call Configured.set(RS_TEMPERATURE);
    call Configured.set(RS_HUMIDITY);
    call Configured.set(RS_DUTY);
    if (nodeType <= NODE_TYPE_WINDOW) { /* battery powered node */
      call Configured.set(RS_VOLTAGE);
    }
    if (nodeType == NODE_TYPE_HEATMETER) { /* heat meter */
      call Configured.set(RS_HM_ENERGY);
      call Configured.set(RS_HM_VOLUME);
      call HMEnergyControl.start();
      call HMVolumeControl.start();
    }
    else if (nodeType == NODE_TYPE_OPTI) { /* energy board */
      call Configured.set(RS_OPTI);
      call OptiControl.start();
    }
    if (nodeType == NODE_TYPE_TEMP) { /* Temp ADC0 */
      call Configured.set(RS_TEMPADC1);
      call Configured.set(RS_DUTY);
    }
    else if (nodeType == NODE_TYPE_GAS) { /* gas board */
      call Configured.set(RS_GAS);
      call GasControl.start();
    }
    else if (nodeType == NODE_TYPE_WINDOW) { /* window board */
      call Configured.set(RS_WINDOW);
    }
    else if (nodeType == CLUSTER_HEAD_CO2_TYPE) { /* clustered CO2 */
      call Configured.set(RS_CO2);
    }
    else if (nodeType == CLUSTER_HEAD_BB_TYPE) { /* clustered BB */
      call Configured.set(RS_CO2);
      call Configured.set(RS_BB);
    }
    else if (nodeType == CLUSTER_HEAD_VOC_TYPE) { /* clustered VOC */
      call Configured.set(RS_CO2);
      call Configured.set(RS_AQ);
      call Configured.set(RS_VOC);
    }
    else if (nodeType == CLUSTER_HEAD_CC_TYPE) { /* current cost */
      call Configured.set(RS_POWER);
    }

#ifndef MISSING_AC_SENSOR
    if (nodeType >= CLUSTER_HEAD_MIN_ID) {
      call Configured.set(RS_AC);
      call ACControl.start();
    }
#endif
    sending = FALSE;

#ifdef DEBUG
    printf("CLUSTER HEAD %u\n", CLUSTER_HEAD);
    printfflush();
#endif
    
    leafMode = ! CLUSTER_HEAD;
    if (CLUSTER_HEAD) 
      call RadioControl.start();

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
      if (last_errno != 1)
	packstate_add(SC_ERRNO, (float) last_errno);
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
	    call ReadVolt.read();
#ifndef MISSING_AC_SENSOR
	  else if (i == RS_AC)
	    call ReadAC.read();
#endif
#ifndef BN
   	  else if (i == RS_POWER)
	    call ReadCC.read();
   	  else if (i == RS_OPTI)
	    call ReadOpti.read();
	  else if (i == RS_HM_ENERGY)
	    call ReadHMEnergy.read();
	  else if (i == RS_HM_VOLUME)
	    call ReadHMVolume.read();
   	  else if (i == RS_GAS)
	    call ReadGas.read();
   	  else if (i == RS_WINDOW)
	    call ReadWindow.read();
   	  else if (i == RS_BB)
	    call ReadBB.read();
#endif
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
#ifndef BN
	if (i == RS_TEMPADC1)
	  call ReadTempADC1.read();
	else
#endif
	if (leafMode)
	  /* if leafMode, avoid polling high power sensors below */
	  call ExpectReadDone.clear(i);
	else if (i == RS_CO2)
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
  
#ifndef MISSING_AC_SENSOR
  event void ReadAC.readDone(error_t result, bool data) {
    leafMode = !data;
    if (!leafMode)
      call RadioControl.start();
    call ExpectReadDone.clear(RS_AC);
    post checkDataGathered();
  }
#endif

#ifndef BN

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
    if (data->x < LOW_VOLTAGE)
      post powerDown();
  }

  event void ReadCC.readDone(error_t result, FilterState* data){
    do_readDone_pass(result, data, RS_POWER, SC_POWER);
  }
  
  event void ReadCO2.readDone(error_t result, FilterState* data){
    do_readDone_filterstate(result, data, RS_CO2, SC_CO2, SC_D_CO2);
  }

  event void ReadBB.readDone(error_t result, FilterState* data){
    do_readDone_filterstate(result, data, RS_BB, SC_BB, SC_D_BB);
  }

  event void ReadAQ.readDone(error_t result, FilterState* data){
    do_readDone_filterstate(result, data, RS_AQ, SC_AQ, SC_D_AQ);
  }

  event void ReadVOC.readDone(error_t result, FilterState* data){
    do_readDone_filterstate(result, data, RS_VOC, SC_VOC, SC_D_VOC);
  }
  
  event void ReadTempADC1.readDone(error_t result, FilterState* data) {
    do_readDone_filterstate(result, data, RS_TEMPADC1, SC_TEMPADC1, SC_D_TEMPADC1);
  }

  event void ReadOpti.readDone(error_t result, FilterState* data) {
    do_readDone_pass(result, data, RS_OPTI, SC_OPTI);
  }
  
  event void ReadHMEnergy.readDone(error_t result, FilterState* data) {
    do_readDone_pass(result, data, RS_HM_ENERGY, SC_HEAT_ENERGY);
  }

  event void ReadHMVolume.readDone(error_t result, FilterState* data) {
    do_readDone_pass(result, data, RS_HM_VOLUME, SC_HEAT_VOLUME);
  }

  event void ReadGas.readDone(error_t result, FilterState* data) {
    do_readDone_pass(result, data, RS_GAS, SC_GAS);
  }

  event void ReadWindow.readDone(error_t result, FilterState* data) {
    do_readDone_pass(result, data, RS_WINDOW, SC_WINDOW);
  }

#endif


#ifdef BN
  void do_readDone_exposure(error_t result, float* data,  uint raw_sensor,  uint state_count, uint state_first){
    int i;

    if (result == SUCCESS){
      for(i = 0; i < state_count; i++){
	packstate_add(state_first+i,data[i]);
      }
    }
    call ExpectReadDone.clear(raw_sensor);
    post checkDataGathered();
  }


  event void ReadTemp.readDone(error_t result, float* data){
    do_readDone_exposure(result, data, RS_TEMPERATURE, SC_BN_TEMP_COUNT, SC_BN_TEMP_FIRST);
  }

  event void ReadHum.readDone(error_t result, float* data){
    do_readDone_exposure(result, data, RS_HUMIDITY, SC_BN_HUM_COUNT, SC_BN_HUM_FIRST);
  }

  event void ReadVolt.readDone(error_t result, float data){
    do_readDone(result, data, RS_VOLTAGE, SC_VOLTAGE);
    if (data < LOW_VOLTAGE)
      post powerDown();
  }

  event void ReadCO2.readDone(error_t result, float* data){
    do_readDone_exposure(result, data, RS_CO2, SC_BN_CO2_COUNT, SC_BN_CO2_FIRST);
  }

  event void ReadAQ.readDone(error_t result, float* data){
    do_readDone_exposure(result, data, RS_AQ, SC_BN_AQ_COUNT, SC_BN_AQ_FIRST);
  }

  event void ReadVOC.readDone(error_t result, float* data){
    do_readDone_exposure(result, data, RS_VOC, SC_BN_VOC_COUNT, SC_BN_VOC_FIRST);
  }
#endif

  /*********** Radio Control *****************/

  event void RadioControl.startDone(error_t ok) {
    if (ok == SUCCESS){
      call CollectionControl.start();
      call DisseminationControl.start();
#ifdef DEBUG
      printf("Radio On %lu\n", call LocalTime.get());
      printfflush();
#endif

      if (call Configured.get(RS_POWER)){
#ifndef BN
	call CurrentCostControl.start();
#endif
      }
      if (!CLUSTER_HEAD || leafMode)
	  sendState();
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
#ifdef BN
    int i;
#endif
#ifdef BLINKY
    call Leds.led2Toggle();
#endif

    if (!CLUSTER_HEAD || leafMode)
      call RadioControl.stop();
 
    call SendTimeOutTimer.stop();

    stop_time = call LocalTime.get();
    //Calculate the next interval
    if (stop_time < send_start_time) // deal with overflow
      send_time = ((UINT32_MAX - send_start_time) + stop_time + 1);
    else
      send_time = (stop_time - send_start_time);
    last_duty = (float) send_time;

    /* the error code has been transmitted and so can now be reset.
       The method of resetting used here allows for errors to have
       occurred between sending the message and receiving
       acknowledgement. */
    if (last_transmitted_errno < last_errno && last_transmitted_errno != 0)
      last_errno = last_errno / last_transmitted_errno;
    else
      last_errno = 1;
   
    my_settings->samplePeriod = DEF_SENSE_PERIOD;
    

#ifndef BN
    call TransmissionControl.transmissionDone();
#endif


#ifdef BN
    for (i = 0; i < RS_SIZE; i++) { 
      if (call Configured.get(i)) {
	if (i == RS_TEMPERATURE)
	  call ReadTemp.transmissionDone();
	else if (i == RS_HUMIDITY)
	  call ReadHum.transmissionDone();
	else if (i == RS_VOLTAGE)
	  call ReadVolt.transmissionDone();
	else if (i == RS_CO2)
	  call ReadCO2.transmissionDone();
	else if (i == RS_AQ)
	  call ReadAQ.transmissionDone();
	else if (i == RS_VOC)
	  call ReadVOC.transmissionDone();
	else
	  continue;
      }
    }
#endif
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
    if (crc == ackMsg->crc)
      if (TOS_NODE_ID == ackMsg->node_id)
	if (expSeq == ackMsg->seq){
	  if (!CLUSTER_HEAD || leafMode)
           call RadioControl.stop();
    	  ackReceived();
    	}
    return;
  }


#ifndef BN
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
#ifdef DEBUG
        printf("sending begun at %lu\n", call LocalTime.get());
        printfflush();
#endif
	sending = TRUE;
      }
    }
      
  }
  
#endif

#ifndef MISSING_AC_SENSOR
  event void ACControl.startDone(error_t error) {}
  
  event void ACControl.stopDone(error_t error) {}
#endif

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
    else if (blink_state >= 60) { /* 30 seconds */
      blinkThrice(FALSE);
    }
    else { 
      blink_state++;
      call BlinkTimer.startOneShot(512L);
      call Leds.set(gray[blink_state % (sizeof gray / sizeof gray[0])]);
    }
  }
  

  
}

