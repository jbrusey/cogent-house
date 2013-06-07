// -*- c -*- 
#include "stdlib.h"

generic module ExposureControllerC(uint8_t num_bands, float threshold) @safe()
{
  provides{
    interface BNController<float*>;
  }

  uses{
    interface Read<float*> as ExposureRead;
  }
}
implementation
{

  float* current_state;
  float sink_state[num_bands];
  bool first = TRUE;
  bool eventful = FALSE;

  command error_t BNController.read(){
    return call ExposureRead.read();
  }
  
  event void ExposureRead.readDone( error_t result, float* data) {  
    uint8_t x;
    float diff;

    //initialse sink state if this is first read
    if (first==TRUE){
      for ( x = 0; x < num_bands; x++ ) {
	sink_state[x]=0;
      }     
    }

    current_state = data;
    
    //Detect event
    for ( x = 0; x < num_bands; x++ ) {
      diff = abs(current_state[x]-sink_state[x]);
      if (first || diff >= threshold) {
	eventful = TRUE;
      }
    }

    signal BNController.readDone(result, current_state);
  }

  command void BNController.transmissionDone(){
    //Successful transmission so clear flag
    eventful = FALSE;
    first = FALSE;

    //update the sink state transmission done
    memcpy(sink_state , current_state, sizeof current_state); 
  }

  command bool BNController.hasEvent(){
    return eventful;
  }

}
