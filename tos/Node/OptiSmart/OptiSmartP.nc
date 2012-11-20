// -*- c -*-
#include "printf.h"
#include "../printfloat.h"

module OptiSmartP
{
  uses {
    interface Boot;
    interface Read<float> as ReadOpti;
    interface SplitControl as OptiControl;
    interface Timer<TMilli> as SensingTimer;
    interface LocalTime<TMilli>;
  }
}

implementation
{

  enum {
    PERIOD = 10240
  };
  
  event void Boot.booted()
  {
    call SensingTimer.startOneShot(PERIOD);
    call OptiControl.start();
  }
  
  event void OptiControl.startDone(error_t error) {
    printf("got start done %u\n", error);
    printfflush();
  }
  
  event void OptiControl.stopDone(error_t error) {
    printf("got stop done %u\n", error);
    printfflush();
  }
  
  
  event void SensingTimer.fired() {
    printf("start read\n");
    call ReadOpti.read();
  }
  
  
  event void ReadOpti.readDone(error_t result, float data) {
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
