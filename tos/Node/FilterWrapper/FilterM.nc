// -*- c -*-
#include "Filter.h"

module FilterM {
  provides {
    interface FilterWrapper<FilterState *> as EstimateCurrentState[uint8_t id];
  }
  uses{		
    interface Read<float> as GetSensorValue[uint8_t id];
    interface Filter[uint8_t id];
    interface LocalTime<TMilli>;
  }
}
implementation {  
  FilterState currentState[RS_SIZE];
  float vals[RS_SIZE][2];

  command void EstimateCurrentState.init[uint8_t id](float a, float b){
    call Filter.init[id](a,b);
  }
  
  command error_t EstimateCurrentState.read[uint8_t id](){
    return call GetSensorValue.read[id]();  //Get Sensor Value (Line 1)
  }

 event void GetSensorValue.readDone[uint8_t id](error_t result, float data) {    //Estimate Current state from filter (Line 2)

   uint32_t time;
   if (result==SUCCESS){
     //get local time
     time = call LocalTime.get(); //Get time (Line 3)
      
     //Get and return current state (Line 4)
     call Filter.filter[id](data, time, &currentState[id]);
     signal EstimateCurrentState.readDone[id](SUCCESS, &currentState[id]);  
   }
   else
     signal EstimateCurrentState.readDone[id](FAIL, NULL);
 }

 /* DEFAULTS */
 default event void EstimateCurrentState.readDone[uint8_t id](error_t result, FilterState* data) {}
 
 default command void Filter.filter[uint8_t id](float z, uint32_t t, FilterState *xnew) {}

 default command void Filter.init[uint8_t id](float a, float b){}

 default command error_t GetSensorValue.read[uint8_t id](){ return FAIL;}
}
       	

