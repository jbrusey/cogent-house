// -*- c -*-
#include "printf.h"
//#include "math.h"
module ExposureTestP @safe()
{
  uses {
    interface Boot;
    interface Exposure<float*> as TempExposure;
    interface Exposure<float*> as HumExposure;
    interface Timer<TMilli> as SenseTimer;
    interface Leds;
  }
}

implementation
{

  bool gothum;
  bool gottemp;
  float* temp;
  float* hum;

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
    call SenseTimer.startPeriodic(10240);
  }

  event void SenseTimer.fired() {
    gothum = FALSE;
    gottemp = FALSE;
    call Leds.led1Toggle();
    call TempExposure.read();
    call HumExposure.read();
  }
  
 task void do_print() {
    if (gothum && gottemp) {

      printfloat2(temp[0]);
      printf(", ");
      printfloat2(temp[1]);
      printf(", ");
      printfloat2(temp[2]);
      printf(", ");
      printfloat2(temp[3]);
      printf(", ");
      printfloat2(temp[4]);
      printf(", ");


      printfloat2(hum[0]);
      printf(", ");
      printfloat2(hum[1]);
      printf(", ");
      printfloat2(hum[2]);
      printf(", ");
      printfloat2(hum[3]);
      printf(", ");

      printf("\n");
      printfflush();
    }
  }


  event void TempExposure.readDone(error_t result, float* data) {
    temp = data;
    gottemp = TRUE;
    post do_print();
  }
  
  event void HumExposure.readDone(error_t result, float* data) {
    hum = data;
    gothum = TRUE;
    post do_print();
  }
    
}
