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
    
    current_state = *data;
    
    //get predicted sink state
    if (! first)
      state_xs = call ValuePredict.predictState(&sink_state, current_state.time);
     
    //no forced send needed so check against the thresh 
    if (first || abs(state_xs - current_state.x) > threshold) 
      signal Read.readDone(SUCCESS, &current_state);
    else 
      signal Read.readDone(FAIL, &current_state);

    first = FALSE;
  }

  command void TransmissionControl.transmissionDone(){
    //update the sink state
    sink_state = current_state;
  }

}
