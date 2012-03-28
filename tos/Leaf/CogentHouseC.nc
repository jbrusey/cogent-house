// -*- c -*-
#include "Packets.h"
#include "PolyClass/horner.c"
#include "CurrentCost/cc_struct.h"
#include "Filter.h"
#include "exposure.h"
#include "HeatMeter/hm_struct.h"
#include <stdio.h>
#include <stdint.h>
#ifdef DEBUG
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#endif 

configuration CogentHouseC {}
implementation
{
  components CogentHouseP, ActiveMessageC, MainC, LedsC, ActiveMessageC as Radio;
#ifdef DEBUG
  components PrintfC;
  components SerialStartC;
#endif
	
  //import timers
  components new TimerMilliC() as SenseTimer;
  components new TimerMilliC() as AckTimeoutTimer;
  components new TimerMilliC() as BlinkTimer;
  components new TimerMilliC() as WarmUpTimer;   
  components RandomC;
  components new AMSenderC(AM_STATEMSG) as StateSender;
  components new AMReceiverC(AM_ACKMSG);

  CogentHouseP.Boot -> MainC.Boot;
  CogentHouseP.StateSender -> StateSender;  
  CogentHouseP.Receive -> AMReceiverC;
  CogentHouseP.SenseTimer -> SenseTimer;
  CogentHouseP.AckTimeoutTimer -> AckTimeoutTimer;
  CogentHouseP.BlinkTimer -> BlinkTimer;
  CogentHouseP.Leds -> LedsC;
  CogentHouseP.RadioControl -> ActiveMessageC;

  //sensing interfaces
  components new SensirionSht11C();
#ifdef SS
  components new HamamatsuS1087ParC() as PAR;
  components new HamamatsuS10871TsrC() as TSR;
#endif SS
  components new VoltageC() as Volt;
  components new CarbonDioxideC() as CarbonDioxide;
  components new VOCC() as VOC;
  components new AQC() as AQ;
  components HplMsp430InterruptP as GIOInterrupt;
  components HplMsp430GeneralIOC as GIO;

  //import sensing modules
  components ThermalSensingM;
#ifdef SS
  components LightSensingM;
#endif SS
  components AirQualityM;
  components BatterySensingM;
  components HeatMeterM;

  //sensor readings
  ThermalSensingM.GetTemp -> SensirionSht11C.Temperature;
  ThermalSensingM.GetHum ->SensirionSht11C.Humidity;
#ifdef SS
  LightSensingM.GetPAR -> PAR;
  LightSensingM.GetTSR -> TSR;
#endif SS
  BatterySensingM.GetVoltage -> Volt;
  AirQualityM.GetCO2 -> CarbonDioxide;
  AirQualityM.GetVOC -> VOC;
  AirQualityM.GetAQ -> AQ;
  AirQualityM.CO2On -> GIO.Port23; //set to gio2
  AirQualityM.WarmUpTimer -> WarmUpTimer;

  HeatMeterM.EnergyInput -> GIO.Port26;
  HeatMeterM.EnergyInterrupt -> GIOInterrupt.Port26; //set to read from gio3
  HeatMeterM.VolumeInput -> GIO.Port23;
  HeatMeterM.VolumeInterrupt -> GIOInterrupt.Port23; //set to read from gio2

  //set up SI filters + event detectors for co2,temp,hum
#ifdef SI
  components new FilterM() as TempFilterWrapper;
  components new EventDetectorC(DEF_TEMP_THRESH) as TempDetector; 
#ifdef KALMAN
  components new KalmanC(0.,0.,FALSE,2.864665e-15,0.000410076, 0.) as TempKalmanC;
  TempFilterWrapper.Filter -> TempKalmanC;
  TempDetector -> TempKalmanC.Predict;
#endif
#ifdef DEWMA
  components new DEWMAC(0., 0., FALSE, DEF_TEMP_ALPHA, DEF_TEMP_BETA) as TempDEWMAC;
  TempFilterWrapper.Filter -> TempDEWMAC;
  TempDetector -> TempDEWMAC.Predict;
#endif
  
  TempFilterWrapper.GetSensorValue -> ThermalSensingM.ReadTemp;
  TempFilterWrapper.LocalTime -> HilTimerMilliC;  
  TempDetector.FilterRead -> TempFilterWrapper.Read;
  components new FilterM() as HumFilterWrapper;
  components new EventDetectorC(DEF_HUM_THRESH) as HumDetector;  
#ifdef KALMAN
  components new KalmanC(0.,0.,FALSE, 2.713816e-13,0.01864952, 0.) as HumKalmanC;
  HumFilterWrapper.Filter -> HumKalmanC;
  HumDetector -> HumKalmanC.Predict;
#endif
#ifdef DEWMA
  components new DEWMAC(0., 0., FALSE, DEF_HUM_ALPHA, DEF_HUM_BETA) as HumDEWMAC;  
  HumFilterWrapper.Filter -> HumDEWMAC;
  HumDetector -> HumDEWMAC.Predict;
#endif

  HumFilterWrapper.GetSensorValue -> ThermalSensingM.ReadHum;
  HumFilterWrapper.LocalTime -> HilTimerMilliC;
  HumDetector.FilterRead -> HumFilterWrapper.Read;
 
  components new FilterM() as CO2FilterWrapper;
  components new EventDetectorC(DEF_CO2_THRESH) as CO2Detector; 
#ifdef KALMAN
  components new KalmanC(0.,0.,FALSE, 5.090581e-10,12.49915, 0.) as CO2KalmanC;
  CO2FilterWrapper.Filter -> CO2KalmanC;
  CO2Detector -> CO2KalmanC.Predict;
#endif
#ifdef DEWMA
  components new DEWMAC(0., 0., FALSE, DEF_CO2_ALPHA, DEF_CO2_BETA) as CO2DEWMAC; 
  CO2FilterWrapper.Filter -> CO2DEWMAC;
  CO2Detector -> CO2DEWMAC.Predict; 
#endif

  CO2FilterWrapper.GetSensorValue -> AirQualityM.ReadCO2;
  CO2FilterWrapper.LocalTime -> HilTimerMilliC;
  CO2Detector.FilterRead -> CO2FilterWrapper.Read;

  //AQ  
  components new FilterM() as AQFilterWrapper;
  components new EventDetectorC(DEF_AQ_THRESH) as AQDetector; 
#ifdef KALMAN
  components new KalmanC(0.,0.,FALSE, 7.276443e-16, 0.003926976 , 0.) as AQKalmanC;
  AQFilterWrapper.Filter -> AQKalmanC;
  AQDetector -> AQKalmanC.Predict;
#endif
#ifdef DEWMA
  components new DEWMAC(0., 0., FALSE, DEF_AQ_ALPHA, DEF_AQ_BETA) as AQDEWMAC; 
  AQFilterWrapper.Filter -> CO2DEWMAC;
  AQDetector -> AQDEWMAC.Predict; 
#endif

  AQFilterWrapper.GetSensorValue -> AirQualityM.ReadAQ;
  AQFilterWrapper.LocalTime -> HilTimerMilliC;
  AQDetector.FilterRead -> AQFilterWrapper.Read;
  
  //VOC
  components new FilterM() as VOCFilterWrapper;
  components new EventDetectorC(DEF_VOC_THRESH) as VOCDetector; 
#ifdef KALMAN
  components new KalmanC(0.,0.,FALSE, 7.276443e-16, 0.003926976 , 0.) as VOCKalmanC;
  VOCFilterWrapper.Filter -> VOCKalmanC;
  VOCDetector -> VOCKalmanC.Predict;
#endif
#ifdef DEWMA
  components new DEWMAC(0., 0., FALSE, DEF_VOC_ALPHA, DEF_VOC_BETA) as VOCDEWMAC; 
  VOCFilterWrapper.Filter -> VOCDEWMAC;
  VOCDetector -> VOCDEWMAC.Predict; 
#endif

  VOCFilterWrapper.GetSensorValue -> AirQualityM.ReadVOC;
  VOCFilterWrapper.LocalTime -> HilTimerMilliC;
  VOCDetector.FilterRead -> VOCFilterWrapper.Read;


  components new FilterM() as VoltageFilterWrapper;
  components new EventDetectorC(0.01) as VoltageDetector;
#ifdef KALMAN
  components new KalmanC(0.,0.,FALSE, 1.032982e-19,8.268842e-6, 0.) as VoltageKalmanC;
  VoltageFilterWrapper.Filter -> VoltageKalmanC;
  VoltageDetector -> VoltageKalmanC.Predict;
#endif
#ifdef DEWMA
  components new DEWMAC(0., 0., FALSE, 0.001, 0.01) as VoltageDEWMAC;
  VoltageFilterWrapper.Filter -> VoltageDEWMAC;
  VoltageDetector -> VoltageDEWMAC.Predict;
#endif

  VoltageFilterWrapper.GetSensorValue -> BatterySensingM.ReadBattery;
  VoltageFilterWrapper.LocalTime -> HilTimerMilliC;
  VoltageDetector.FilterRead -> VoltageFilterWrapper.Read;

  //Add in the event detecors
  
  //link modules to main file
  CogentHouseP.ReadTemp -> TempDetector.Read;
  CogentHouseP.TempTrans -> TempDetector.TransmissionControl;
  CogentHouseP.ReadHum -> HumDetector.Read;
  CogentHouseP.HumTrans -> HumDetector.TransmissionControl;
  CogentHouseP.ReadVolt -> VoltageDetector.Read;
  CogentHouseP.VoltTrans -> VoltageDetector.TransmissionControl;
  CogentHouseP.ReadCO2 -> CO2Detector.Read;
  CogentHouseP.CO2Trans -> CO2Detector.TransmissionControl;
  
  CogentHouseP.ReadAQ -> AQDetector.Read;
  CogentHouseP.AQTrans -> AQDetector.TransmissionControl;
  
  CogentHouseP.ReadVOC -> VOCDetector.Read;
  CogentHouseP.VOCTrans -> VOCDetector.TransmissionControl;

  components new BitVectorC(RS_SIZE) as ExpectSendDone;
  CogentHouseP.ExpectSendDone -> ExpectSendDone.BitVector; 
#endif

#ifdef BN  
  //Temp
  components new ExposureEventDetectorC(TEMP_BAND_LEN,DEF_TEMP_BAND_THRESH) as TempDetector;
  components new ExposureC(TEMP_BAND_LEN, RS_TEMPERATURE, DEF_GAMMA) as TempExposure;
  
  TempExposure.GetValue -> ThermalSensingM.ReadTemp;
  TempDetector.ExposureRead -> TempExposure.Read;
  CogentHouseP.ReadTemp -> TempDetector.Read;
  CogentHouseP.TempTrans -> TempDetector.TransmissionControl;

  //Hum
  components new ExposureEventDetectorC(HUM_BAND_LEN,DEF_HUM_BAND_THRESH) as HumDetector;
  components new ExposureC(HUM_BAND_LEN, RS_HUMIDITY, DEF_GAMMA) as HumExposure;
  
  HumExposure.GetValue -> ThermalSensingM.ReadHum;
  HumDetector.ExposureRead -> HumExposure.Read;
  CogentHouseP.ReadHum -> HumDetector.Read;
  CogentHouseP.HumTrans -> HumDetector.TransmissionControl;

  //Hum
  components new ExposureEventDetectorC(CO2_BAND_LEN,DEF_CO2_BAND_THRESH) as CO2Detector;
  components new ExposureC(CO2_BAND_LEN, RS_CO2, DEF_GAMMA) as CO2Exposure;
  
  CO2Exposure.GetValue -> AirQualityM.ReadCO2;
  CO2Detector.ExposureRead -> CO2Exposure.Read;
  CogentHouseP.ReadCO2 -> CO2Detector.Read;
  CogentHouseP.CO2Trans -> CO2Detector.TransmissionControl;

  components new BitVectorC(RS_SIZE) as ExpectSendDone;
  CogentHouseP.ExpectSendDone -> ExpectSendDone.BitVector; 

  CogentHouseP.ReadAQ->AirQualityM.ReadAQ;
  CogentHouseP.ReadVOC->AirQualityM.ReadVOC;

  BatterySensingM.GetVoltage -> Volt;
  CogentHouseP.ReadVolt->BatterySensingM.ReadBattery;
#endif

#ifdef SS
  CogentHouseP.ReadTemp->ThermalSensingM.ReadTemp;
  CogentHouseP.ReadHum->ThermalSensingM.ReadHum;
  CogentHouseP.ReadPAR->LightSensingM.ReadPAR;
  CogentHouseP.ReadTSR->LightSensingM.ReadTSR;
  CogentHouseP.ReadVolt->BatterySensingM.ReadBattery;
  CogentHouseP.ReadCO2->AirQualityM.ReadCO2;
  CogentHouseP.ReadVOC->AirQualityM.ReadVOC;
  CogentHouseP.ReadAQ->AirQualityM.ReadAQ;
#endif  

  components HilTimerMilliC;
	
  CogentHouseP.LocalTime -> HilTimerMilliC;

  // current cost
  components CurrentCostM,CurrentCostSerialC;
  components new TimerMilliC() as TimeoutTimer;
  components new TimerMilliC() as ResumeTimer;
  components new TimerMilliC() as FirstByteTimer;

  CurrentCostM.CurrentCostUartStream -> CurrentCostSerialC;
  CurrentCostM.UartControl -> CurrentCostSerialC;
  CurrentCostM.TimeoutTimer -> TimeoutTimer;
  CurrentCostM.ResumeTimer -> ResumeTimer;
  CurrentCostM.FirstByteTimer -> FirstByteTimer;
  CurrentCostM.Leds -> LedsC;
  CurrentCostM.LocalTime -> HilTimerMilliC;
  
  CogentHouseP.ReadWattage->CurrentCostM.ReadWattage;
  CogentHouseP.CurrentCostControl -> CurrentCostM.CurrentCostControl;

  //Heat Meter
  CogentHouseP.ReadHeatMeter->HeatMeterM.ReadHeatMeter;
  CogentHouseP.HeatMeterControl -> HeatMeterM.HeatMeterControl;


  //Configured
  //Need to define right size
  components new AccessibleBitVectorC(RS_SIZE) as Configured;
  CogentHouseP.Configured -> Configured.AccessibleBitVector;

  //expectReadDone
  components new BitVectorC(RS_SIZE) as ExpectReadDone;
  CogentHouseP.ExpectReadDone -> ExpectReadDone.BitVector;


  //PackState
  components new PackStateC(SC_SIZE) as PackState;
  components new AccessibleBitVectorC(SC_SIZE) as ABV;

  PackState.Mask -> ABV;
  CogentHouseP.PackState -> PackState;

}
