// -*- c -*-
#include "printf.h"
#include <stdint.h>
#define HIGH_COVARIANCE 1e20
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
  void printfloat2( float v) {
    int i = (int) v;
    int j;

    if (isnan(v)) {
      printf("nan");
      return;
    }
    if (isinf(v)) {
      printf("inf");
      return;
    }

    if (v < 0) {
      printf("-");
      printfloat2(-v);
      return;
    }
    if (v > 1e9) {
      printf("big");
      return;
    }

    printf("%d.", i);

    v -= i;

    j = 0;
    while (j < 20 && v > 0.) {
      v *= 10.;
      i = (int) v;
      v -= i;
      printf("%d", i);  
      j ++;
    }
  }


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

    printfloat2(data->x);
    printf(", ");
    printfloat2(data->dx);
    printf(", ");
    printfloat2(data->z);
    printf("\n");
    printfflush();
    gottemp = TRUE;
  }

  
}
