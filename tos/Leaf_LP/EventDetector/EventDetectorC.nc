// -*- c -*- 
#include "Filter.h"
#include "stdlib.h"
#include "EventDetector.h"

module EventDetectorC @safe()
{
  provides interface TransmissionControl[uint8_t id];
  provides interface Read<FilterState *>[uint8_t id];
  uses interface Read<FilterState *> as FilterRead;
  uses interface Predict as ValuePredict;
}
implementation
{
  FilterState current_state [EVENT_DETECTOR_MAX];
  FilterState sink_state [EVENT_DETECTOR_MAX];
  bool first [EVENT_DETECTOR_MAX];
  float threshold [EVENT_DETECTOR_MAX];

  command error_t Read.read[uint8_t id](){
    return call FilterRead.read();
  }
  
  event void FilterRead.readDone(error_t result, FilterState* data) {
    float state_xs;
    
    if (result == SUCCESS) {
      current_state[id] = *data;
    
      //get predicted sink state
      if (! first[id])
	state_xs = call ValuePredict.predictState(&sink_state[id], current_state[id].time);
     
      //no forced send needed so check against the thresh 
      if (first[id] || abs(state_xs - current_state[id].x) > threshold[id]) 
	signal Read.readDone[id](SUCCESS, &current_state[id]);
      else 
	signal Read.readDone[id](FAIL, NULL);

      first[id] = FALSE;
    }
    else
      signal Read.readDone[id](FAIL, NULL);
  }

  command void TransmissionControl.init[uint8_t id](float t){
    first[id] = TRUE;
    threshold[id] = t;
  }

  command void TransmissionControl.transmissionDone[uint8_t id](){
    //update the sink state
    sink_state[id] = current_state[id];
  }

}
