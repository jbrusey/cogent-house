// -*- c -*-
#include "printf.h"
#include "printfloat.h"
module ACReaderP
{
  uses {
    interface Boot;
    interface Read<bool> as ReadAC;
    interface StdControl as ACControl;
    interface Timer<TMilli> as SensingTimer;
    interface LocalTime<TMilli>;
    interface Leds;
  }
}

implementation
{

  enum {
    PERIOD = 2048
  };
  
  event void Boot.booted()
  {
    error_t error;
    printf("Boot\n");
    printfflush();
    error = call ACControl.start();
    printf("got start result %u\n", error);
    printfflush();
    call ReadAC.read();
    call SensingTimer.startPeriodic(PERIOD);
  }
  
  event void SensingTimer.fired() {
    printf("start read\n");
    call ReadAC.read();
  }
  
  
  event void ReadAC.readDone(error_t result, bool data) {
    if (result == SUCCESS) {
      printf("State: ");
      printfloat(data);
      printf("\n");
    }
    else
      printf("readDone no data\n");
    printfflush();      
  }
}
