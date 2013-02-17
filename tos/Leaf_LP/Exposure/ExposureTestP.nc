// -*- c -*-
#include "printf.h"
//#include "math.h"
#include "Packets.h"
module ExposureTestP @safe()
{
  uses {
    interface Boot;
    interface Read<float*> as TempExposure;
    interface Read<float*> as HumExposure;
    interface Read<float*> as CO2Exposure;
    interface Timer<TMilli> as SenseTimer;
    interface Leds;

    interface Read<float> as ReadAQ;
    interface Read<float> as ReadVOC;
  }
}

implementation
{

  bool gothum;
  bool gottemp;
  bool gotCO2;
  bool gotVolt;
  float* temp;
  float* hum;
  float* CO2;

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
    call SenseTimer.startPeriodic(30720);
  }

  event void SenseTimer.fired() {
    gothum = FALSE;
    gottemp = FALSE;
    gotCO2 = FALSE;
    call Leds.led1Toggle();
    call TempExposure.read();
    call HumExposure.read();
    call CO2Exposure.read();
  }
  
 task void do_print() {
    if (gothum && gottemp && gotCO2) {

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

      printfloat2(CO2[0]);
      printf(", ");
      printfloat2(CO2[1]);
      printf(", ");
      printfloat2(CO2[2]);
      printf(", ");
      printfloat2(CO2[3]);

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
  
  event void CO2Exposure.readDone(error_t result, float* data) {
    CO2 = data;
    gotCO2 = TRUE;
    post do_print();
  }

  event void ReadVOC.readDone(error_t result, float data) {   
  }
  
  event void ReadAQ.readDone(error_t result, float data) {   
  }
  

}
