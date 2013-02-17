// -*- c -*-
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#include "minunit.h"
#include <stdint.h>
#include "../PolyClass/horner.c"
#include "exposure.h"


configuration ExposureTestC {}

implementation
{
  components MainC, ExposureTestP;
  components PrintfC;
  components SerialStartC;
  components LedsC;
  components new SensirionSht11C();
  components new CarbonDioxideC() as CarbonDioxide;
  components HplMsp430InterruptP;
  components HplMsp430GeneralIOC as GPIO;
  components new VOCC() as VOC;
  components new AQC() as AQ; 

  components ThermalSensingM;
  components AirQualityM;

  components new TimerMilliC() as SenseTimer;
  components HilTimerMilliC;
  components new TimerMilliC() as WarmUpTimer;  

  components new ExposureC(TEMP_BAND_LEN, RS_TEMPERATURE, 0.9999868213) as TempExposure;
  components new ExposureC(HUM_BAND_LEN, RS_HUMIDITY, 0.9999868213) as HumExposure;
  components new ExposureC(CO2_BAND_LEN, RS_CO2, 0.9999868213) as CO2Exposure;

  ThermalSensingM.GetTemp -> SensirionSht11C.Temperature;
  ThermalSensingM.GetHum -> SensirionSht11C.Humidity;
  AirQualityM.GetCO2 -> CarbonDioxide;
  AirQualityM.CO2On -> GPIO.Port23;
  AirQualityM.WarmUpTimer -> WarmUpTimer;
  AirQualityM.GetVOC -> VOC;
  AirQualityM.GetAQ -> AQ; 

  TempExposure.GetValue -> ThermalSensingM.ReadTemp;
  HumExposure.GetValue -> ThermalSensingM.ReadHum;
  CO2Exposure.GetValue -> AirQualityM.ReadCO2;

  ExposureTestP.Boot -> MainC.Boot;
  ExposureTestP.TempExposure -> TempExposure.Read;
  ExposureTestP.HumExposure -> HumExposure.Read;
  ExposureTestP.CO2Exposure -> CO2Exposure.Read;

  ExposureTestP.ReadAQ -> AirQualityM.ReadAQ;
  ExposureTestP.ReadVOC -> AirQualityM.ReadVOC;

  ExposureTestP.Leds -> LedsC;
  ExposureTestP.SenseTimer -> SenseTimer;

}

