// -*- c -*-
#include "printf.h"
#include "printfloat.h"
module PulseReaderP
{
  uses {
    interface Boot;
    interface Read<float> as ReadPulse;
    interface SplitControl as PulseControl;
    interface Timer<TMilli> as SensingTimer;
    interface LocalTime<TMilli>;
    interface Leds;
  }
}

implementation
{

  enum {
    PERIOD = 10240
  };
  
  event void Boot.booted()
  {
    printf("Boot\n");
    call SensingTimer.startOneShot(PERIOD);
    call PulseControl.start();
  }
  
  event void PulseControl.startDone(error_t error) {
    printf("got start done %u\n", error);
    printfflush();
  }
  
  event void PulseControl.stopDone(error_t error) {
    printf("got stop done %u\n", error);
    printfflush();
  }
  
  
  event void SensingTimer.fired() {
    printf("start read\n");
    call ReadPulse.read();
  }
  
  
  event void ReadPulse.readDone(error_t result, float data) {
    if (result == SUCCESS) {
      printf("interupt count: ");
      printfloat(data);
      printf("\n");
    }
    else
      printf("readDone no data\n");
    
    printfflush();
    call SensingTimer.startOneShot(PERIOD);
  }
}
