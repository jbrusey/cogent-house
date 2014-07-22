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
    interface SIPController<FilterState *> as ReadWallTemp;
    interface SIPController<FilterState *> as ReadWallHum;
    interface TransmissionControl;
    interface StdControl as OptiControl;
    interface StdControl as GasControl;
    interface StdControl as WindowControl;
    interface SplitControl as CurrentCostControl;
    interface StdControl as HMEnergyControl;
    interface StdControl as HMVolumeControl;
   
#ifndef MISSING_AC_SENSOR
    interface Read<bool> as ReadAC;
    interface StdControl as ACControl;
#endif
    
    //Bitmask and packstate
    interface AccessibleBitVector as Configured;
    interface BitVector as ExpectReadDone;
    interface PackState;
  }
}
implementation
{
  uint32_t sample_period;

  uint8_t nodeType;   /* default node type is determined by top 4 bits of node_id */
  bool sending;
  bool shutdown = FALSE;
  bool first_period_pending = FALSE;
  bool clustered = FALSE;
#ifdef CLUSTER_BASED
  bool clustered = TRUE;
  bool leaf_mode = FALSE;
  bool send_state_pending = FALSE;
#endif
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

  /** prototypes **/
  void radioStop(void);

/********* Boot Message Methods **********/
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
      newData->special = 0xc7;
      newData->clustered = clustered;

      memcpy(newData->version, DEF_HG_REVISION, sizeof(newData->version) - 1);

      if (call BootSender.send(&dataMsg, message_size) == SUCCESS) {
#ifdef DEBUG
	  printf("boot sending begun at %lu\n", call LocalTime.get());
	  printfflush();
#endif
      }
    }
  }

  event void BootSender.sendDone(message_t *msg, error_t ok) {
#ifdef DEBUG
    printf("Boot sending done at %lu\n", call LocalTime.get());
    printfflush();
#endif
  }

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


      if (call Configured.get(RS_POWER)){
        call CurrentCostControl.start();
      }


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
#ifdef CLUSTER_BASED
    error_t radio_status;
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
	
    	if (call TransmissionControl.hasEvent()) {
#ifdef CLUSTER_BASED
	  if (leaf_mode) {
	    /* if running in leaf_mode, radio may not be turned on, so
	       we mark it to be turned on and set a flag to say that a
	       send is pending */
	    send_state_pending = TRUE;
	    radio_status = call RadioControl.start();
	    if (radio_status == EALREADY) {
	      send_state_pending = FALSE;
	      sendState();
	    }
	  }
	  else
#endif /* CLUSTER_BASED */
	    sendState();
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

  event void SendTimeOutTimer.fired() {
    sample_period = DEF_BACKOFF_SENSE_PERIOD;

#ifdef DEBUG
    printf("ack receving failed %lu\n", call LocalTime.get());
    printf("Sample Period to be used %lu\n", sample_period);
    printfflush();
#endif
#ifdef CLUSTER_BASED
    if (leaf_mode)
      radioStop();
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
    call ReadWallTemp.init(SIP_WALL_TEMP_MASK, SIP_WALL_TEMP_THRESH, SIP_WALL_TEMP_ALPHA, SIP_WALL_TEMP_BETA);
    call ReadWallHum.init(SIP_WALL_HUM_MASK, SIP_WALL_HUM_THRESH, SIP_WALL_HUM_ALPHA, SIP_WALL_HUM_BETA);

    nodeType = TOS_NODE_ID >> 12;
    sample_period = DEF_SENSE_PERIOD;
#ifdef CLUSTER_BASED
    leaf_mode = ! CLUSTER_HEAD;
#endif

    // Configure the node for attached sensors.

    call Configured.clearAll();
    call Configured.set(RS_TEMPERATURE);
    call Configured.set(RS_HUMIDITY);
    call Configured.set(RS_DUTY);
    call Configured.set(RS_VOLTAGE);
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
      call WindowControl.start();
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
    else if (nodeType == CLUSTER_HEAD_WALL_TYPE) { /* wall temp/moisture sensor */
      call Configured.set(RS_WALL_TEMP);
      call Configured.set(RS_WALL_HUM); 
    }

#ifndef MISSING_AC_SENSOR
    if (CLUSTER_HEAD) {
      call Configured.set(RS_AC);
      call ACControl.start();
    }
#endif
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
	if (i == RS_TEMPADC1)
	  call ReadTempADC1.read();
	else if (i == RS_WALL_TEMP)
	  call ReadWallTemp.read();
	else if (i == RS_WALL_HUM)
	  call ReadWallHum.read();
#ifdef CLUSTER_BASED
	else if (leaf_mode)
	  /* if leaf_mode, avoid polling high power sensors below */
	  call ExpectReadDone.clear(i);
#endif

	else if (i == RS_CO2)
	  call ReadCO2.read();
	else if (i == RS_AQ)
	  call ReadAQ.read();
	else if (i == RS_VOC)
	  call ReadVOC.read();
	else if (i == RS_BB)
	    call ReadBB.read();
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
#ifdef CLUSTER_BASED
    /* if were in leaf mode and we now receive power, start radio */
    if (data && leaf_mode) 
      call RadioControl.start();
    leaf_mode = ! data;
#endif
    call ExpectReadDone.clear(RS_AC);
    post checkDataGathered();
  }
#endif


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
  
  event void ReadWallTemp.readDone(error_t result, FilterState* data) {
    do_readDone_filterstate(result, data, RS_WALL_TEMP, SC_WALL_TEMP, SC_D_WALL_TEMP);
  }

  event void ReadWallHum.readDone(error_t result, FilterState* data) {
    do_readDone_filterstate(result, data, RS_WALL_HUM, SC_WALL_HUM, SC_D_WALL_HUM);
  }

  /*********** Radio Control *****************/

  event void RadioControl.startDone(error_t ok) {
    if (ok == SUCCESS){
      call CollectionControl.start();
      call DisseminationControl.start();
      if (first_period_pending) {
	call SenseTimer.startOneShot(DEF_FIRST_PERIOD);
	first_period_pending = FALSE;
	sendBoot();
      }
#ifdef DEBUG
      printf("Radio On %lu\n", call LocalTime.get());
      printfflush();
#endif

      if (call Configured.get(RS_POWER)){
	call CurrentCostControl.start();
      }
#ifdef CLUSTER_BASED
      if (leaf_mode && send_state_pending) {
	send_state_pending = FALSE;
	sendState();
      }
#endif
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
    
#ifdef CLUSTER_BASED
    if (leaf_mode)
      radioStop();
#endif

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

