// -*- c -*- 
#include "Filter.h"

generic module EventDetectorC(float threshold) @safe()
{
  provides interface TransmissionControl;
  provides interface Read<FilterState *>;
  uses interface Read<FilterState *> as FilterRead;
  uses interface Predict as ValuePredict;
}
implementation
{
  FilterState current_state, sink_state;
  bool first = TRUE;
  bool transmitExpected = FALSE;
  int periodsToHeartbeat=HEARTBEAT_PERIOD;

  command error_t Read.read(){
    return call FilterRead.read();
  }
  
  float abs(float f) {
    if (f < 0)
      return -f;
    else 
      return f;
  }

  event void FilterRead.readDone( error_t result, FilterState* data) {
    float state_xs;
    
    if (first==TRUE){
      sink_state.time=0;
      sink_state.z=0.;
      sink_state.x=0.;
      sink_state.dx=0.;
      first = FALSE;
    }

    current_state = *data;

    //read done so decrease periods To Heartbeat
    periodsToHeartbeat=periodsToHeartbeat-1;

    if (periodsToHeartbeat==0){
      transmitExpected = TRUE;
    }

    
    //get predicted sink state
    state_xs = call ValuePredict.predictState(&sink_state, current_state.time);
     
    //last packet not sent so trigger a send
    if (transmitExpected == TRUE) {
      signal Read.readDone(SUCCESS, &current_state);
    }
    //no forced send needed so check against the thresh 
    else if (abs(state_xs - current_state.x) > threshold){
      signal Read.readDone(SUCCESS, &current_state);
      transmitExpected = TRUE;
    }
    else signal Read.readDone(FAIL, &current_state);

  }

  command void TransmissionControl.transmissionDone(){
    //Successful transmission so clear flag
    transmitExpected = FALSE;

    //reset heartbeat period
    periodsToHeartbeat=HEARTBEAT_PERIOD;

    //update the sink state
    sink_state = current_state;
  }

}
