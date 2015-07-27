/* -*- c -*- */
#include "Timer.h"
module SwitchedAnalogTestP
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
    printf("booted\n");
    printfflush();
    call MilliTimer.startPeriodic(20 * 1024);
  }

  //When timer is fired get sensor readings
  event void MilliTimer.fired() {
    printf("starting read\n");
    printfflush();
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

