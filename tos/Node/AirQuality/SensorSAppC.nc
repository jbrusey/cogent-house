#define NEW_PRINTF_SEMANTICS
#include "printf.h"

configuration SensorSAppC {}

implementation {

  components MainC;

  //define components that will be used
  components SensorSC as App, LedsC;
  components new SensirionSht11C(); 
  components new TimerMilliC();
  components PrintfC;
  components SerialStartC;

  components new CarbonDioxideC() as CarbonDioxide;
  components new VOCC() as VOC;
  components new AQC() as AQ;

  components AirQualityM;
  components new TimerMilliC() as WarmUpTimer;

  //pulse interfaces
  components HplMsp430InterruptP;
  components HplMsp430GeneralIOC as GIOC;

  //Wire componants to app
	
  App.Boot -> MainC;
  App.Leds ->  LedsC;
  App.MilliTimer -> TimerMilliC;
  AirQualityM.GetCO2 -> CarbonDioxide;
  AirQualityM.GetVOC -> VOC;
  AirQualityM.GetAQ -> AQ;
  AirQualityM.CO2On -> GIOC.Port23;
  AirQualityM.WarmUpTimer -> WarmUpTimer;
  App.ReadCO2->AirQualityM.ReadCO2;
  App.ReadVOC->AirQualityM.ReadVOC;
  App.ReadAQ->AirQualityM.ReadAQ;

}
