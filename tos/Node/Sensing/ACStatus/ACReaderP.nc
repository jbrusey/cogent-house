// -*- c -*-
#include "printf.h"
#include "printfloat.h"
module ACReaderP
{
  uses {
    interface Boot;
    interface Read<bool> as ReadAC;
    interface SplitControl as ACControl;
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
    printf("Boot\n");
    printfflush();
    call ACControl.start();
  }
  
  event void ACControl.startDone(error_t error) {
    printf("got start done %u\n", error);
    printfflush();
    call ReadAC.read();
    call SensingTimer.startPeriodic(PERIOD);
  }
  
  event void ACControl.stopDone(error_t error) {
    printf("got stop done %u\n", error);
    printfflush();
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
