// -*- c -*-
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#include "minunit.h"
#include "../Sensing/PolyClass/horner.c"
#include "SIPController.h"
#include <stdio.h>
#include <stdint.h>

configuration DEWMAWrapperTestC {}

implementation
{
  components MainC, DEWMAWrapperTestP;
  components FilterM;

  components DEWMAC as DEWMA;
  
  components PrintfC;
  components SerialStartC;
  
  components new SensirionSht11C();
	
  components ThermalSensingM;
  
  components new TimerMilliC() as SenseTimer;
  components HilTimerMilliC;  

  DEWMAWrapperTestP.Boot -> MainC.Boot; 
  DEWMAWrapperTestP.SenseTimer -> SenseTimer;

  ThermalSensingM.GetTemp -> SensirionSht11C.Temperature;
  ThermalSensingM.GetHum -> SensirionSht11C.Humidity;
  
  
  FilterM.Filter[0] -> DEWMA.Filter[0];
  FilterM.GetSensorValue[0] -> ThermalSensingM.ReadTemp;
  FilterM.LocalTime -> HilTimerMilliC;
  DEWMAWrapperTestP.TempRead ->FilterM.EstimateCurrentState[0];

 
  FilterM.GetSensorValue[1] -> ThermalSensingM.ReadHum;
 

}

