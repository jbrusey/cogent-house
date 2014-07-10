// -*- c -*- 
#include <stdlib.h>

module SIPControllerM @safe()
{
  provides{
    interface TransmissionControl;
    interface SIPController<FilterState *>[uint8_t id];
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
  bool mask [RS_SIZE];
  bool eventful [RS_SIZE];
  bool read_started [RS_SIZE];
  float threshold [RS_SIZE];

  command error_t Init.init() {
    int i;
    for (i = 0; i < RS_SIZE; i++) 
      read_started[i] = FALSE;
    return SUCCESS;
  }

  

  command error_t SIPController.read[uint8_t id](){
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
      signal SIPController.readDone[id](SUCCESS, &current_state[id]); //Read has been successful so return SUCESS and the state
      first[id] = FALSE;
	
    }
    else
      signal SIPController.readDone[id](FAIL, NULL);
  }
  
  command void SIPController.init[uint8_t id](float thresh, bool sensorMask, float a, float b){
    first[id] = TRUE;
    threshold[id] = thresh;
    mask[id] = sensorMask;
    
    call EstimateCurrentState.init[id](a, b);
    call Heartbeat.init();
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


 default event void SIPController.readDone[uint8_t id](error_t result, FilterState* data) {}
 default command error_t EstimateCurrentState.read[uint8_t id](){ return SUCCESS;}
 default command void EstimateCurrentState.init[uint8_t id](float a, float b){}

}
