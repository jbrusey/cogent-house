// -*- c -*-
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#include "minunit.h"
#include "mat22.h"
#include "../PolyClass/horner.c"
#include <stdio.h>
#include <stdint.h>

configuration DEWMAWrapperTestC {}

implementation
{
  components MainC, DEWMAWrapperTestP;
  components new FilterM() as TempFilterWrapper;
  components new FilterM() as HumFilterWrapper;
  components new FilterM() as CO2FilterWrapper;
  components new FilterM() as VoltageFilterWrapper;


  components new DEWMAC(0., 0., FALSE, 0.2, 0.2) as TempDEWMAC;
  components new DEWMAC(0., 0., FALSE, 0.2, 0.2) as HumDEWMAC;
  components new DEWMAC(0., 0., FALSE, 0.2, 0.2) as CO2DEWMAC;
  components new DEWMAC(0., 0., FALSE, 0.2, 0.2) as VoltageDEWMAC;
  
  
  components PrintfC;
  components SerialStartC;
  
  components new SensirionSht11C();
  components new VoltageC() as Volt;
  components new CarbonDioxideC() as CarbonDioxide;
  components HplMsp430InterruptP;
  components HplMsp430GeneralIOC as GPIO;
  components new VOCC() as VOC;
  components new AQC() as AQ;  
	
  components ThermalSensingM;
  components AirQualityM;
  components BatterySensingM;
  
  components new TimerMilliC() as SenseTimer;
  components HilTimerMilliC;
  components new TimerMilliC() as WarmUpTimer;   
  components RandomC;


  DEWMAWrapperTestP.ReadAQ -> AirQualityM.ReadAQ;
  DEWMAWrapperTestP.ReadVOC -> AirQualityM.ReadVOC;

  ThermalSensingM.GetTemp -> SensirionSht11C.Temperature;
  ThermalSensingM.GetHum -> SensirionSht11C.Humidity;
  BatterySensingM.GetVoltage -> Volt;
  AirQualityM.GetCO2 -> CarbonDioxide;
  AirQualityM.CO2On -> GPIO.Port23;
  AirQualityM.WarmUpTimer -> WarmUpTimer;
  AirQualityM.GetVOC -> VOC;
  AirQualityM.GetAQ -> AQ;
  
  
  TempFilterWrapper.Filter -> TempDEWMAC;
  TempFilterWrapper.GetSensorValue -> ThermalSensingM.ReadTemp;
  TempFilterWrapper.LocalTime -> HilTimerMilliC;
  DEWMAWrapperTestP.TempRead->TempFilterWrapper.Read;
  DEWMAWrapperTestP.TempPredict->TempDEWMAC.Predict;

  
  HumFilterWrapper.Filter -> HumDEWMAC;
  HumFilterWrapper.GetSensorValue -> ThermalSensingM.ReadHum;
  HumFilterWrapper.LocalTime -> HilTimerMilliC;
  DEWMAWrapperTestP.HumRead->HumFilterWrapper.Read;
  DEWMAWrapperTestP.HumPredict->HumDEWMAC.Predict;


  CO2FilterWrapper.Filter -> CO2DEWMAC;
  CO2FilterWrapper.GetSensorValue -> AirQualityM.ReadCO2;
  CO2FilterWrapper.LocalTime -> HilTimerMilliC;
  DEWMAWrapperTestP.CO2Read->CO2FilterWrapper.Read;
  DEWMAWrapperTestP.CO2Predict->CO2DEWMAC.Predict;
  
  VoltageFilterWrapper.Filter -> VoltageDEWMAC;
  VoltageFilterWrapper.GetSensorValue -> BatterySensingM.ReadBattery;
  VoltageFilterWrapper.LocalTime -> HilTimerMilliC;
  DEWMAWrapperTestP.VoltRead->VoltageFilterWrapper.Read;
  DEWMAWrapperTestP.VoltPredict->VoltageDEWMAC.Predict;


  DEWMAWrapperTestP.Boot -> MainC.Boot; 
  DEWMAWrapperTestP.SenseTimer -> SenseTimer;

  

}

