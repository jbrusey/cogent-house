// -*- c -*-

module CogentHouseP
{
  uses {
    //low-level stuff
    interface Timer<TMilli> as SenseTimer;
    interface Timer<TMilli> as SendTimeoutTimer;
    interface Timer<TMilli> as BlinkTimer;
    interface Leds;
    interface Boot;
    
    //radio
    interface SplitControl as RadioControl;
    interface LowPowerListening;
    
    //ctp
    interface StdControl as CollectionControl;
    interface CtpInfo;

#ifdef DISSEMINATE		
    // dissemination
    interface StdControl as DisseminationControl;
    interface DisseminationValue<ConfigMsg> as SettingsValue;
#endif
		
    //sending interfaces
    interface Send as StateSender;
    
    //Sensing
    interface Read<float> as ReadTemp;
    interface Read<float> as ReadHum;
    interface Read<uint16_t> as ReadPAR;
    interface Read<uint16_t> as ReadTSR;
    interface Read<uint16_t> as ReadVolt;
    interface Read<float> as ReadCO2;
    interface Read<float> as ReadVOC;
    interface Read<float> as ReadAQ;
    interface SplitControl as OptiControl;
    interface Read<float> as ReadOpti;
    interface SplitControl as CurrentCostControl;
    interface Read<ccStruct *> as ReadWattage;
    interface SplitControl as HeatMeterControl;
    interface Read<hmStruct *> as ReadHeatMeter;
    interface Read<float> as ReadTempADC1;
    interface Read<float> as ReadTempADC2;
    interface Read<float> as ReadBlackBulb;

    //Bitmask and packstate
    interface AccessibleBitVector as Configured;
    interface BitVector as ExpectReadDone;
    interface PackState;
    
    //Time
    interface LocalTime<TMilli>;

    // Logging
    /* interface LogWrite as DebugLog; */
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
  };

  //variables
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
  uint16_t message_size;

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
      call PackState.add(SC_DUTY_TIME, last_duty);
    if (last_errno != 1.) {
      call PackState.add(SC_ERRNO, last_errno);
    }
    last_transmitted_errno = last_errno;
    pslen = call PackState.pack(&ps);
			
    message_size = sizeof (StateMsg) - (SC_SIZE - pslen) * sizeof (float);
    newData = call StateSender.getPayload(&dataMsg, message_size);
    if (newData != NULL) { 
      //newData->tos_node_id = TOS_NODE_ID;
      newData->special = 0xc7;
      newData->ctp_parent_id = -1;
      newData->timestamp = call LocalTime.get();
      if (call CtpInfo.getParent(&parent) == SUCCESS) { 
      	newData->ctp_parent_id = parent;
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
      call Configured.set(RS_DUTY);
    }
    else if (nodeType == 1) { /* current cost */
      call Configured.set(RS_TEMPERATURE);
      call Configured.set(RS_HUMIDITY);
      call Configured.set(RS_DUTY);
      call Configured.set(RS_POWER);
      //powered so set to always be awake
      call LowPowerListening.setLocalWakeupInterval(0);
    } 
    else if (nodeType == 2) { /* co2 */
      call Configured.set(RS_TEMPERATURE);
      call Configured.set(RS_HUMIDITY);
      call Configured.set(RS_CO2);
      call Configured.set(RS_DUTY);
      //powered so set to always be awake      
      call LowPowerListening.setLocalWakeupInterval(0);
    }
    else if (nodeType == 3) { /* air quality */
      call Configured.set(RS_TEMPERATURE);
      call Configured.set(RS_HUMIDITY);
      call Configured.set(RS_CO2);
      call Configured.set(RS_AQ);
      call Configured.set(RS_VOC);
      call Configured.set(RS_DUTY);
      //powered so set to always be awake      
      call LowPowerListening.setLocalWakeupInterval(0);
    }
    else if (nodeType == 4) { /* heat meter */
      call Configured.set(RS_HEATMETER);
      call Configured.set(RS_VOLTAGE);
    }
    else if (nodeType == 5) { /* opti smart */
      call Configured.set(RS_OPTI);
      call Configured.set(RS_VOLTAGE);
      call OptiControl.start();
    }
    else if (nodeType == 6) { /* window sensor */
      call Configured.set(RS_TEMPERATURE);
      call Configured.set(RS_HUMIDITY);
      call Configured.set(RS_TEMPADC1);
      call Configured.set(RS_TEMPADC2);
      call Configured.set(RS_VOLTAGE);
      call Configured.set(RS_DUTY);
    }
    else if (nodeType == 7) { /* black bulb */
      call Configured.set(RS_TEMPERATURE);
      call Configured.set(RS_HUMIDITY);
      call Configured.set(RS_BLACKBULB);
      call Configured.set(RS_VOLTAGE);
      call Configured.set(RS_DUTY);
    }

    call RadioControl.start();
    
    call BlinkTimer.startOneShot(512L); /* start blinking to show that we are up and running */
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
	sendState();
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

    call SendTimeoutTimer.startOneShot(30L*1024L); // 30 sec sense/send timeout
    if (my_settings->blink)
      call Leds.led1On();

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
	  else if (i == RS_OPTI)
	    call ReadOpti.read();
	  else if (i == RS_TEMPADC1)
	    call ReadTempADC1.read();
	  else if (i == RS_TEMPADC2)
	    call ReadTempADC2.read();
	  else if (i == RS_BLACKBULB)
	    call ReadBlackBulb.read();
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

  event void ReadVolt.readDone(error_t result, uint16_t data) {	
    do_readDone(result,((data/4096.)*3), RS_VOLTAGE, SC_VOLTAGE);
  }
  
  event void ReadTempADC1.readDone(error_t result, float data) {
    do_readDone(result, data, RS_TEMPADC1, SC_TEMPADC1);
  }

  event void ReadTempADC2.readDone(error_t result, float data) {
    do_readDone(result, data, RS_TEMPADC2, SC_TEMPADC2);
  }
  
  event void ReadBlackBulb.readDone(error_t result, float data) {
    do_readDone(result, data, RS_BLACKBULB, SC_BLACKBULB);
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
    do_readDone(result, data, RS_OPTI, SC_POWER_PULSE);
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


 /* Once the radio starts, start the collection protocol. */
  event void RadioControl.startDone(error_t ok) {
    if (ok == SUCCESS)
      {
#ifdef DEBUG
        printf("Radio On\n");
        printfflush();
#endif
	sending = FALSE;
	call CollectionControl.start();
#ifdef DISSEMINATE
	call DisseminationControl.start();
#endif
	call SenseTimer.startOneShot(DEF_FIRST_PERIOD);
	if (call Configured.get(RS_POWER)) 
	  call CurrentCostControl.start();
	if (call Configured.get(RS_HEATMETER)) 
	  call HeatMeterControl.start();
      }
    else
      call RadioControl.start();
  }


  //Empty methods
  event void RadioControl.stopDone(error_t ok) { }

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
#ifdef DEBUG
    printf("restartSenseTimer at %lu\n", call LocalTime.get());
    printfflush();
#endif
    if (stop_time < sense_start_time) // deal with overflow
      send_time = ((UINT32_MAX - sense_start_time) + stop_time + 1);
    else
      send_time = (stop_time - sense_start_time);
    last_duty = (float) send_time;
    
    if (my_settings->samplePeriod < send_time)
      next_interval = 0;
    else
      next_interval = my_settings->samplePeriod - send_time;

    call SenseTimer.startOneShot(next_interval);

    if (my_settings->blink)
      call Leds.led1Off();
  }

  /** When a message has been successfully transmitted, this event is
      triggered. At this point, we stop the timeout timer, restart the
      sense timer and restart the current-cost if it is needed.
  */
  event void StateSender.sendDone(message_t *msg, error_t ok) {
    sending = FALSE;

    call SendTimeoutTimer.stop();

    if (ok != SUCCESS) 
      reportError(ERR_SEND_FAILED);    
    else {
      if (last_transmitted_errno < last_errno && last_transmitted_errno != 0.)
	last_errno = last_errno / last_transmitted_errno;
      else
	last_errno = 1.;
    }

    restartSenseTimer();

    if (call Configured.get(RS_POWER))
      call CurrentCostControl.start();
  }

  /** sending has taken too long and so we should stop trying
   */
  event void SendTimeoutTimer.fired() {
    if (call StateSender.cancel(&dataMsg) == SUCCESS) 
      sending = FALSE;
    else {
      reportError(ERR_SEND_CANCEL_FAIL);
    }
    reportError(ERR_SEND_TIMEOUT);
    restartSenseTimer();
  }


#ifdef DISSEMINATE  
  /** SettingsValue.changed
   *
   * - triggered when new settings are disseminated
   * - update settings and turn on current-cost if needed
   * - adjust sample period timer
   */
  event void SettingsValue.changed() { 
    uint8_t i;
#ifdef DEBUG
    uint8_t j;
    unsigned char *ns;
#endif
    uint32_t offset;
    bool oldBlink = my_settings->blink;
    const ConfigMsg *newSettings = call SettingsValue.get();
    

    if (newSettings->special != SPECIAL) {
#ifdef DEBUG
      printf("corrupt:");
      ns = (unsigned char *) newSettings;
      for (i = 0; i < sizeof (ConfigMsg); i++) {
	printf("%02x", ns[i]);
      }
      printf("\n");
      printfflush();
#endif
      return;
    }

#ifdef DEBUG
    printf("settings: tc=%u %02x\n", newSettings->typeCount, newSettings->special);
    for (i = 0; i < newSettings->typeCount; i++) {
      if (settings.byType[i].blink != newSettings->byType[i].blink)
	printf("b->%d t%u\n", newSettings->byType[i].blink, i);
      if (settings.byType[i].samplePeriod != newSettings->byType[i].samplePeriod)
	printf("per->%lu t%u\n", newSettings->byType[i].samplePeriod, i);
      for (j = 0; j < bitset_size(RS_SIZE); j++) { 
	if (settings.byType[i].configured[j] != newSettings->byType[i].configured[j])
	  printf("cfg[%u]->%01x t%u\n", 
		 j, 
		 newSettings->byType[i].configured[j], 
		 i);
      }
    }
    printfflush();
#endif

    /* new settings are only valid up to typeCount which may be less
       than nodeType, so only copy up to typeCount */
    for (i = 0; i < newSettings->typeCount; i++) {
      settings.byType[i] = newSettings->byType[i];
    }
      
    if (oldBlink && !my_settings->blink) {
      call Leds.set(0); // turn all off
    }

    // need to manually copy out configured
    for (i = 0; i < call Configured.getArrayLength(); i++)
      call Configured.setArrayElement(i,my_settings->configured[i]);

    
    if (call Configured.get(RS_POWER))
      call CurrentCostControl.start();
    else
      call CurrentCostControl.stop();

  }
  
#endif /* DISSEMINATE */


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
      if (call StateSender.send(&dataMsg, message_size) == SUCCESS) {
	sending = TRUE;
      }
    }

  }

  event void OptiControl.startDone(error_t error) { }
  
  event void OptiControl.stopDone(error_t error) {}  
  
}
