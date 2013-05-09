// -*- c -*-
#include "printf.h"
#include "cc_struct.h"
#include "printfloat.h"

module CurrentCostP
{
  uses {
    interface Boot;
    interface Read<ccStruct *> as ReadWattage;
    interface SplitControl as CurrentCostControl;
    interface Timer<TMilli> as SensingTimer;
    interface LocalTime<TMilli>;
  }
}

implementation
{
  bool sensing = TRUE;

  enum {
    PERIOD = 30720
  };

  event void Boot.booted()
  {
    call SensingTimer.startOneShot(10240);
    call CurrentCostControl.start();
  }

  event void CurrentCostControl.startDone(error_t error) {
    printf("got start done %u\n", error);
    printfflush();
  }

  event void CurrentCostControl.stopDone(error_t error) {
    printf("got stop done %u\n", error);
    printfflush();
    call SensingTimer.startOneShot(512); 
  }

	
  event void SensingTimer.fired() {
    if (sensing) { 
      printf("start read\n");
      call ReadWattage.read();
      sensing = FALSE;
    }
    else {
      printf("requested start\n");
      call CurrentCostControl.start();
      sensing = TRUE;
      call SensingTimer.startOneShot(PERIOD - 512);
    }
  }
	

  event void ReadWattage.readDone(error_t result, ccStruct *data) {
    if (result == SUCCESS) {
      printfloat(data->min);
      printf(", ");
      printfloat(data->average);
      printf(", ");
      printfloat(data->max);
      printf(", ");
      printfloat(data->kwh);
      printf("\n");
    }
    else
      printf("readDone no data\n");

    printfflush();
    printf("requested stop\n");
    call CurrentCostControl.stop();
  }
}
