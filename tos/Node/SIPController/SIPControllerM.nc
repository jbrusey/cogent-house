// -*- c -*- 
#include <stdlib.h>

module SIPControllerM @safe()
{
  provides{
    interface TransmissionControl;
    interface Read<FilterState *> as Sensor[uint8_t id];
    interface Init;
  }

  uses{
    interface Heartbeat;
    interface Predict as SinkStatePredict;
    interface FilterWrapper<FilterState *> as EstimateCurrentState[uint8_t id];
  }
}
implementation
{

  FilterState current_state [RS_SIZE];
  FilterState sink_state [RS_SIZE];
  bool first [RS_SIZE];
  /* TODO: find a way to put mapping for sensor types in one place */
  bool mask [RS_SIZE] = {
      SIP_TEMP_MASK,
      SIP_HUM_MASK,
      SIP_VOLTAGE_MASK,
      SIP_ADC_0_MASK,
      SIP_ADC_1_MASK,
      SIP_ADC_2_MASK,
      SIP_ADC_3_MASK,
      SIP_ADC_6_MASK,
      SIP_ADC_7_MASK,
      SIP_PAR_MASK,
      SIP_TSR_MASK,
      SIP_GIO2_MASK,
      SIP_GIO3_MASK };
  bool eventful [RS_SIZE];
  bool read_started [RS_SIZE];
  float threshold [RS_SIZE] = {
      SIP_TEMP_THRESH,
      SIP_HUM_THRESH,
      SIP_VOLTAGE_THRESH,
      SIP_ADC_0_THRESH,
      SIP_ADC_1_THRESH,
      SIP_ADC_2_THRESH,
      SIP_ADC_3_THRESH,
      SIP_ADC_6_THRESH,
      SIP_ADC_7_THRESH,
      SIP_PAR_THRESH,
      SIP_TSR_THRESH,
      SIP_GIO2_THRESH,
      SIP_GIO3_THRESH };

  float alpha [RS_SIZE] = {
      SIP_TEMP_ALPHA,
      SIP_HUM_ALPHA,
      SIP_VOLTAGE_ALPHA,
      SIP_ADC_0_ALPHA,
      SIP_ADC_1_ALPHA,
      SIP_ADC_2_ALPHA,
      SIP_ADC_3_ALPHA,
      SIP_ADC_6_ALPHA,
      SIP_ADC_7_ALPHA,
      SIP_PAR_ALPHA,
      SIP_TSR_ALPHA,
      SIP_GIO2_ALPHA,
      SIP_GIO3_ALPHA };

  float beta [RS_SIZE] = {
      SIP_TEMP_BETA,
      SIP_HUM_BETA,
      SIP_VOLTAGE_BETA,
      SIP_ADC_0_BETA,
      SIP_ADC_1_BETA,
      SIP_ADC_2_BETA,
      SIP_ADC_3_BETA,
      SIP_ADC_6_BETA,
      SIP_ADC_7_BETA,
      SIP_PAR_BETA,
      SIP_TSR_BETA,
      SIP_GIO2_BETA,
      SIP_GIO3_BETA };

  command error_t Init.init() {
    int i;

    for (i = 0; i < RS_SIZE; i++) {
      read_started[i] = FALSE;
      first[i] = TRUE;
      call EstimateCurrentState.init[i](alpha[i], beta[i]);
    }
    call Heartbeat.init();


    return SUCCESS;
  }

  

  command error_t Sensor.read[uint8_t id](){
    read_started[id] = TRUE;
    return call EstimateCurrentState.read[id]();       //Get state estimate (line 1-3)
  }
  
  event void EstimateCurrentState.readDone[uint8_t id](error_t result, FilterState* data) {
    float y;
    float state_xs =0.;
    
    if (! read_started[id])
      return;

    read_started[id] = FALSE;

    if (result == SUCCESS) {
      current_state[id] = *data;


      if (! first[id])
	state_xs = call SinkStatePredict.predictState(&sink_state[id], current_state[id].time);  //Predict current sink state (line 4)
      y = abs(state_xs - current_state[id].x);  //Calculate state difference (line 5)

      if (first[id] || (mask[id] * y) >= threshold[id] || call Heartbeat.triggered())     //Detect event check if first or event or heartbeat (line 6)
	eventful[id] = TRUE;
      signal Sensor.readDone[id](SUCCESS, &current_state[id]); //Read has been successful so return SUCESS and the state
      first[id] = FALSE;
	
    }
    else
      signal Sensor.readDone[id](FAIL, NULL);
  }
  

  command void TransmissionControl.transmissionDone(){
    int i;

    //Reset Eventful
    for (i = 0; i < RS_SIZE; i++){
      eventful[i] = FALSE;
    }

    //update the sink state transmission done
    memcpy(sink_state , current_state, sizeof current_state); 
    call Heartbeat.reset();
  }
  
  
  command bool TransmissionControl.hasEvent(){
    int i;
    for (i = 0; i < RS_SIZE; i++){
      if (eventful[i]==TRUE){
        return TRUE;
     }
    }
    return FALSE;
  }


 default event void Sensor.readDone[uint8_t id](error_t result, FilterState* data) {}
 default command error_t EstimateCurrentState.read[uint8_t id](){ return SUCCESS;}
 default command void EstimateCurrentState.init[uint8_t id](float a, float b){}

}
