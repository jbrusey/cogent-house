#include "Timer.h"
module AnalogTestP
{
  //setup and define the interfaces that will be used
  uses
    {
      interface Timer<TMilli> as MilliTimer;
      interface Boot;
      interface Leds;
      interface Read<float> as ReadFloat;
    }
}
implementation
{

  //Start the node
  event void Boot.booted()
  {
    call MilliTimer.startPeriodic(1024);
  }

  //When timer is fired get sensor readings
  event void MilliTimer.fired() {
    call ReadFloat.read();
  }




  event void ReadFloat.readDone(error_t result, float data) {
    if (result == SUCCESS) { 
      printf("value: ");
      printfloat(data);
      printf("\n");
      printfflush();
    }
    else {
      printf("read failed\n");
      printfflush();
    }
  }

}

