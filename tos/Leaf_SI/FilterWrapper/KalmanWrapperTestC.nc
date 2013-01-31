// -*- c -*-
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#include "minunit.h"
#include "mat22.h"
#include "../PolyClass/horner.c"

configuration KalmanWrapperTestC {}

implementation
{
  components MainC, KalmanWrapperTestP;
  components new FilterM(0.01) as TempFilterWrapper;
  components new FilterM(0.03) as HumFilterWrapper;
  components new FilterM(4.0) as CO2FilterWrapper;
  components new FilterM(0.0004) as VoltageFilterWrapper;

  components new KalmanC(0.,0.,FALSE, 2.864665e-14,0.0004100762, 0.) as TempKalmanC;
  components new KalmanC(0.,0.,FALSE, 2.713816e-12,0.01864952, 0.) as HumKalmanC;
  components new KalmanC(0.,0.,FALSE, 5.090581e-10,12.49915, 0.) as CO2KalmanC;
  components new KalmanC(0.,0.,FALSE, 1.032982e-19,8.268842e-6, 0.) as VoltageKalmanC;
  components PrintfC;
  components SerialStartC;
  
  components new SensirionSht11C();
  components new VoltageC() as Volt;
  components new CarbonDioxideC() as CarbonDioxide;
  components HplMsp430InterruptP;
  components HplMsp430GeneralIOC as GPIO;
	
  components ThermalSensingM;
  components AirQualityM;
  components BatterySensingM;
  
  components new TimerMilliC() as SenseTimer;
  components HilTimerMilliC;
  components new TimerMilliC() as WarmUpTimer;   
  components RandomC;

  ThermalSensingM.GetTemp -> SensirionSht11C.Temperature;
  ThermalSensingM.GetHum -> SensirionSht11C.Humidity;
  BatterySensingM.GetVoltage -> Volt;
  AirQualityM.GetCO2 -> CarbonDioxide;
  AirQualityM.CO2On -> GPIO.Port23;
  AirQualityM.WarmUpTimer -> WarmUpTimer;
  
  TempFilterWrapper.Filter -> TempKalmanC;
  TempFilterWrapper.GetSensorValue -> ThermalSensingM.ReadTemp;
  TempFilterWrapper.LocalTime -> HilTimerMilliC;
  TempFilterWrapper.Random -> RandomC;
  KalmanWrapperTestP.TempRead->TempFilterWrapper.Read;
  KalmanWrapperTestP.TempPredict->TempKalmanC.Predict;

  
  HumFilterWrapper.Filter -> HumKalmanC;
  HumFilterWrapper.GetSensorValue -> ThermalSensingM.ReadHum;
  HumFilterWrapper.LocalTime -> HilTimerMilliC;
  HumFilterWrapper.Random -> RandomC;
  KalmanWrapperTestP.HumRead->HumFilterWrapper.Read;
  KalmanWrapperTestP.HumPredict->HumKalmanC.Predict;


  CO2FilterWrapper.Filter -> CO2KalmanC;
  CO2FilterWrapper.GetSensorValue -> AirQualityM.ReadCO2;
  CO2FilterWrapper.LocalTime -> HilTimerMilliC;
  CO2FilterWrapper.Random -> RandomC;
  KalmanWrapperTestP.CO2Read->CO2FilterWrapper.Read;
  KalmanWrapperTestP.CO2Predict->CO2KalmanC.Predict;
  
  VoltageFilterWrapper.Filter -> VoltageKalmanC;
  VoltageFilterWrapper.GetSensorValue -> BatterySensingM.ReadBattery;
  VoltageFilterWrapper.LocalTime -> HilTimerMilliC;
  VoltageFilterWrapper.Random -> RandomC;
  KalmanWrapperTestP.VoltRead->VoltageFilterWrapper.Read;
  KalmanWrapperTestP.VoltPredict->VoltageKalmanC.Predict;


  KalmanWrapperTestP.Boot -> MainC.Boot; 
  KalmanWrapperTestP.SenseTimer -> SenseTimer;

  

}

