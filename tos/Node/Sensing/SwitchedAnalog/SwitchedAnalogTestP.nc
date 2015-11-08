
/* -*- c -*- */
#include "Timer.h"
module SwitchedAnalogTestP
{
  //setup and define the interfaces that will be used
  uses
    {
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
    printf("starting read\n");
    printfflush();
    call ReadFloat.read();
  }

}

