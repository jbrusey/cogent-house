// -*- c -*- 
#include "stdlib.h"

generic module ExposureEventDetectorC(uint8_t num_bands, float threshold) @safe()
{
  provides interface TransmissionControl;
  provides interface Read<float*>;
  uses interface Read<float*> as ExposureRead;
}
implementation
{
  float* currentPct;
  float prevPct[num_bands];
  bool first = TRUE;
  bool transmitExpected = FALSE;

  command error_t Read.read(){
    return call ExposureRead.read();
  }
  
  
  event void ExposureRead.readDone( error_t result, float* data) {  
    uint8_t x;
    float diff;
    error_t res=FAIL;

    if (first==TRUE){
      first=FALSE;
      for ( x = 0; x < num_bands; x++ ) {
	prevPct[x]=0;
      }     
    }

    currentPct = data;
    
    //last packet not sent so trigger a send
    if (transmitExpected == TRUE) {
      signal Read.readDone(SUCCESS, currentPct);
    }
    //no forced send needed so check against the thresh 
    else if (transmitExpected==FALSE){
      for ( x = 0; x < num_bands; x++ ) {
	diff = abs(currentPct[x]-prevPct[x]);
	if (diff >=threshold) {
	  res=SUCCESS;
	  transmitExpected = TRUE;
	}
      }
    }
    //no need to update
    signal Read.readDone(res, currentPct);
  }

  command void TransmissionControl.transmissionDone(){
    uint8_t x;
    //Successful transmission so clear flag
    transmitExpected = FALSE;

    //update the sink state
    for ( x = 0; x < num_bands; x++ ) {
      prevPct[x]=currentPct[x];
    }
  }

}
