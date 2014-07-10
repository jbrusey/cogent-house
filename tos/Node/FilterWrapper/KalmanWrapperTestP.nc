// -*- c -*-
#include "printf.h"
#include "printfloat.h"
#include <stdint.h>
#define HIGH_COVARIANCE 1e20
#include "Filter.h"
#include <stdlib.h>

module KalmanWrapperTestP @safe()
{
  uses {
    interface Boot;
    interface Read<FilterState *> as TempRead;
    interface Predict as TempPredict;
    interface Read<FilterState *> as HumRead;
    interface Predict as HumPredict;
    interface Read<FilterState *> as CO2Read;
    interface Predict as CO2Predict;
    interface Read<FilterState *> as VoltRead;
    interface Predict as VoltPredict;
    interface Timer<TMilli> as SenseTimer;
  }
}

implementation
{

  event void Boot.booted()
  {
    call SenseTimer.startPeriodic(30720);
  }

  bool gothum;
  bool gottemp;
  bool gotCO2;
  bool gotVolt;
  FilterState CO2, volt, temp, hum, last_temp, last_hum, last_volt, last_CO2;
  
  event void SenseTimer.fired() {
    gothum = FALSE;
    gottemp = FALSE;
    gotCO2 = FALSE;
    gotVolt = FALSE;
    call TempRead.read();
    call HumRead.read();
    call CO2Read.read();
    call VoltRead.read();
  }
  
  
  task void do_print() {
    float temp_xs, hum_xs, volt_xs, CO2_xs;
    bool temp_event = FALSE, 
      hum_event = FALSE,
      volt_event = FALSE,
      CO2_event = FALSE;

    if (gothum && gottemp && gotCO2 && gotVolt) {

      temp_xs = call TempPredict.predictState(&last_temp, temp.time);
      if (abs(temp_xs - temp.x) > 0.1) {
	last_temp = temp;
	temp_event = TRUE;
      }
      hum_xs = call HumPredict.predictState(&last_hum, hum.time);
      if (abs(hum_xs - hum.x) > 1) { 
	last_hum = hum;
	hum_event = TRUE;
      }

      volt_xs = call VoltPredict.predictState(&last_volt, volt.time);
      if (abs(volt_xs - volt.x) > 0.05) { 
	last_volt = volt;
	volt_event = TRUE;
      }

      CO2_xs = call CO2Predict.predictState(&last_CO2, CO2.time);
      if (abs(CO2_xs - CO2.x) > 500) { 
	last_CO2 = CO2;
	CO2_event = TRUE;
      }

      printf("%lu, %d, %d, %d, %d, ", temp.time, temp_event, hum_event, CO2_event, volt_event);
      printfloat(temp.x);
      printf(", ");
      printfloat(temp.dx);
      printf(", ");
      printfloat(temp.z);
      printf(", ");
      printfloat(temp_xs);
      printf(", ");

      printfloat(hum.x);
      printf(", ");
      printfloat(hum.dx);
      printf(", ");
      printfloat(hum.z);
      printf(", ");
      printfloat(hum_xs);
      printf(", ");

      printfloat(CO2.x);
      printf(", ");
      printfloat(CO2.dx);
      printf(", ");
      printfloat(CO2.z);
      printf(", ");
      printfloat(CO2_xs);
      printf(", ");

      printfloat(volt.x);
      printf(", ");
      printfloat(volt.dx);
      printf(", ");
      printfloat(volt.z);
      printf(", ");
      printfloat(volt_xs);

      printf("\n");
      printfflush();
    }
  }

  event void TempRead.readDone(error_t result, FilterState* data) {
    temp = *data;
    gottemp = TRUE;
    post do_print();
  }
  
  event void HumRead.readDone(error_t result, FilterState* data) {
    hum = *data;
    gothum = TRUE;
    post do_print();
  }
  
  event void CO2Read.readDone(error_t result, FilterState* data) {
    CO2 = *data;
    gotCO2= TRUE;
    post do_print();
  }
  
  event void VoltRead.readDone(error_t result, FilterState* data) {
    volt = *data;
    gotVolt = TRUE;
    post do_print();
  }

}
