// -*- c -*-
#include "printf.h"
#include "hm_struct.h"
#include "../printfloat.h"

module HeatMeterP
{
  uses {
    interface Boot;
    interface Read<hmStruct *> as ReadHeatMeter;
    interface SplitControl as HeatMeterControl;
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
    call HeatMeterControl.start();
  }
  
  event void HeatMeterControl.startDone(error_t error) {
    printf("got start done %u\n", error);
    printfflush();
  }
  
  event void HeatMeterControl.stopDone(error_t error) {
    printf("got stop done %u\n", error);
    printfflush();
  }
  
  
  event void SensingTimer.fired() {
    printf("start read\n");
    call ReadHeatMeter.read();
  }
  
  
  event void ReadHeatMeter.readDone(error_t result, hmStruct *data) {
    if (result == SUCCESS) {
      printfloat(data->energy);
      printf(", ");
      printfloat(data->volume);
      printf("\n");
    }
    else
      printf("readDone no data\n");
    
    printfflush();
    call SensingTimer.startOneShot(PERIOD);
  }
}
