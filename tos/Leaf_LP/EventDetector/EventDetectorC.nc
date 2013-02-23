// -*- c -*- 
#include "Filter.h"
#include "stdlib.h"

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
  
  event void FilterRead.readDone( error_t result, FilterState* data) {
    if (result==SUCCESS){
      float state_xs;
      
      current_state = *data;
      
      //get predicted sink state
      if (! first)
	state_xs = call ValuePredict.predictState(&sink_state, current_state.time);
     
      //no forced send needed so check against the thresh 
      if (first || abs(state_xs - current_state.x) > threshold) 
	signal Read.readDone(SUCCESS, &current_state);
      else 
	signal Read.readDone(FAIL, NULL);

      first = FALSE;
    }
    else
      signal Read.readDone(FAIL, NULL);
  }

  command void TransmissionControl.transmissionDone(){
    //update the sink state
    sink_state = current_state;
  }

}
