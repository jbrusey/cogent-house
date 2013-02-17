// -*- c -*- 
#include "stdlib.h"

module LowBatteryC
{
  provides{
    interface BNController<float>;
  }

  uses{
    interface Read<float> as BatteryRead;
  }
}
implementation
{
  bool eventful = FALSE;
  float lowVoltage = 2.3;

  command error_t BNController.read(){
    return call BatteryRead.read();
  }
  
  
  event void BatteryRead.readDone( error_t result, float data) {  
  
    if (result == SUCCESS){
        if (data < lowVoltage)
            eventful = TRUE;
    }
    signal BNController.readDone(result, data);
  }




  command void BNController.transmissionDone(){
    //Successful transmission so clear flag
    eventful = FALSE;
  }


  command bool BNController.hasEvent(){
    return eventful;
  }

}
