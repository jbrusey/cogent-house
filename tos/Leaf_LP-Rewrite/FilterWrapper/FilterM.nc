// -*- c -*-
#include "mat22.h"
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

  command void EstimateCurrentState.init[uint8_t id](float x_init, float dx_init, bool init_set, float a, float b){
    call Filter.init[id](x_init,dx_init,init_set,a,b);
  }
  
  command error_t EstimateCurrentState.read[uint8_t id](){
    return call GetSensorValue.read[id]();  //Get Sensor Value (Line 1)
  }

 event void GetSensorValue.readDone[uint8_t id](error_t result, float data) {    //Estimate Current state from filter (Line 2)

   uint32_t time;
   if (result==SUCCESS){
     //get local time
     time = call LocalTime.get(); //Get time (Line 3)
     currentState[id].z = data;
      
     //Get and return current state (Line 4)
     call Filter.filter[id](data, time, vals[id]);
     currentState[id].time = time;
     currentState[id].x = vals[id][0];
     currentState[id].dx = vals[id][1];
     signal EstimateCurrentState.readDone[id](SUCCESS, &currentState[id]);  
   }
   else
     signal EstimateCurrentState.readDone[id](FAIL, NULL);
 }

 /* DEFAULTS */
 default event void EstimateCurrentState.readDone[uint8_t id](error_t result, FilterState* data) {}
 
 default command void Filter.filter[uint8_t id](float z, uint32_t t, vec2 v) {}

 default command void Filter.init[uint8_t id](float x_init, float dx_init, bool init_set, float a, float b){}

 default command error_t GetSensorValue.read[uint8_t id](){ return SUCCESS;}
}
       	

