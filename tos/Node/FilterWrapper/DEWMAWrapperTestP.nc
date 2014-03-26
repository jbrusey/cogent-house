// -*- c -*-
#include "printf.h"
#include "printfloat.h"
#include <stdint.h>
#include "Filter.h"

module DEWMAWrapperTestP @safe()
{
  uses {
    interface Boot;
    interface FilterWrapper<FilterState *> as TempRead;
    interface Timer<TMilli> as SenseTimer; 
  }
}

implementation
{
  event void Boot.booted()
  {
    call TempRead.init(0.1, 0.1);
    call SenseTimer.startPeriodic(1024);
    //initialise filter
  }

  FilterState volt, temp, hum, last_temp, last_hum, last_volt;
  bool gottemp = FALSE;

  
  event void SenseTimer.fired() {
    //printf("Read\n");
    //printfflush();
    gottemp = FALSE;
    call TempRead.read();
  }
  
  
  event void TempRead.readDone(error_t result, FilterState* data) {

    printfloat(data->x);
    printf(", ");
    printfloat(data->dx);
    printf(", ");
    printfloat(data->z);
    printf("\n");
    printfflush();
    gottemp = TRUE;
  }

  
}
