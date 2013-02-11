// -*- c -*-
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#include "minunit.h"
#include <stdint.h>
#include "../PolyClass/horner.c"
#include "../../Packets.h"
#include "exposure.h"


configuration ExposureTestC {}

implementation
{
  components MainC, ExposureTestP;
  components PrintfC;
  components SerialStartC;
  components LedsC;
  components new SensirionSht11C();

  components ThermalSensingM;

  components new TimerMilliC() as SenseTimer;
  components HilTimerMilliC;
  components new TimerMilliC() as WarmUpTimer;  

  components ExposureC;

  ThermalSensingM.GetTemp -> SensirionSht11C.Temperature;
  ThermalSensingM.GetHum -> SensirionSht11C.Humidity;

  ExposureC.GetSensorValue[0] -> ThermalSensingM.ReadTemp;
  ExposureC.GetSensorValue[1] -> ThermalSensingM.ReadHum;

  ExposureTestP.Boot -> MainC.Boot;
  ExposureTestP.TempExposure -> ExposureC.Exposure[0];
  ExposureTestP.HumExposure -> ExposureC.Exposure[1];


  ExposureTestP.Leds -> LedsC;
  ExposureTestP.SenseTimer -> SenseTimer;

}

