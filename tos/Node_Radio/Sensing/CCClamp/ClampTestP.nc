// -*- c -*-
#include "printf.h"
#include "printfloat.h"
#include "clamp_struct.h"

module ClampTestP
{
  uses {
    interface Boot;
    interface Read<clampStruct *> as ReadClamp;
    interface SplitControl as ClampControl;
    interface Timer<TMilli> as SensingTimer;
    interface LocalTime<TMilli>;
  }
}

implementation
{

  uint32_t PERIOD = 61440L;
  
  event void Boot.booted()
  {
    call SensingTimer.startOneShot(PERIOD);
    call ClampControl.start();
  }
  
  event void ClampControl.startDone(error_t error) {
    printf("got start done %u\n", error);
    printfflush();
  }
  
  event void ClampControl.stopDone(error_t error) {
    printf("got stop done %u\n", error);
    printfflush();
  }
  
  
  event void SensingTimer.fired() {
    printf("start read\n");
    call ReadClamp.read();
  }
  
  
  event void ReadClamp.readDone(error_t result, clampStruct *data) {
    if (result == SUCCESS) {
      printf("Min: ");
      printfloat(data->min);
      printf("\n");
      printf("Average: ");
      printfloat(data->average);
      printf("\n");
      printf("Max: ");
      printfloat(data->max);
      printf("\n");
    }
    else
      printf("readDone no data\n");
    
    printfflush();
    call SensingTimer.startOneShot(PERIOD);
  }
}
