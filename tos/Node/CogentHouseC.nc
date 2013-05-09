// -*- c -*-
#include "../Packets.h"
#include "Collection.h"
#include "./Sensing/PolyClass/horner.c"
#include "./Sensing/CurrentCost/cc_struct.h"
#include "Filter.h"
#include "./Exposure/exposure.h"
#include "./Sensing/HeatMeter/hm_struct.h"
#include <stdint.h>
#ifdef DEBUG
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#endif 

configuration CogentHouseC {}
implementation
{

  /************* MAIN COMPONENTS ***********/
  
  components MainC, CogentHouseP, LedsC, HilTimerMilliC;
#ifdef DEBUG
  components PrintfC, SerialStartC;
#endif

  CogentHouseP.Boot -> MainC.Boot; 
  CogentHouseP.Leds -> LedsC;
  CogentHouseP.LocalTime -> HilTimerMilliC;
  
  //Timers
  components new TimerMilliC() as SenseTimer;
  components new TimerMilliC() as BlinkTimer;
  components new TimerMilliC() as WarmUpTimer;
  components new TimerMilliC() as SendTimeOutTimer;

  CogentHouseP.SenseTimer -> SenseTimer;
  CogentHouseP.BlinkTimer -> BlinkTimer;
  CogentHouseP.SendTimeOutTimer -> SendTimeOutTimer;

  // Instantiate and wire our collection service
  components CollectionC, ActiveMessageC;
  components new CollectionSenderC(AM_STATEMSG) as StateSender;

  CogentHouseP.RadioControl -> ActiveMessageC;
  CogentHouseP.CollectionControl -> CollectionC;
  CogentHouseP.CtpInfo -> CollectionC;
  CogentHouseP.StateSender -> StateSender;
  
  //LPL
  CogentHouseP.LowPowerListening -> ActiveMessageC;

  //Configured
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

  //sensing interfaces
  components new SensirionSht11C();
  components new VoltageC() as Volt;
  components new CarbonDioxideC() as CarbonDioxide;
  components new VOCC() as VOC;
  components new AQC() as AQ;
  components HplMsp430InterruptP as GIOInterrupt;
  components HplMsp430GeneralIOC as GIO;
  components new Temp_ADC1C() as Temp_ADC1;

  //Sensing Modules
  components ThermalSensingM, AirQualityM, BatterySensingM, TempADCM;

  //Wire up Sensing
  ThermalSensingM.GetTemp -> SensirionSht11C.Temperature;
  ThermalSensingM.GetHum ->SensirionSht11C.Humidity;
  BatterySensingM.GetVoltage -> Volt;
  AirQualityM.GetCO2 -> CarbonDioxide;
  AirQualityM.GetVOC -> VOC;
  AirQualityM.GetAQ -> AQ;
  AirQualityM.CO2On -> GIO.Port23; //set to gio2
  AirQualityM.WarmUpTimer -> WarmUpTimer;
#ifdef SIP
  components PulseReaderM;
  PulseReaderM.EnergyInput -> GIO.Port26;
  PulseReaderM.EnergyInterrupt -> GIOInterrupt.Port26; //set to read from gio3
#endif
  TempADCM.GetTempADC1 -> Temp_ADC1;

  /*********** ACK CONFIG *************/

  components DisseminationC;
  components new DisseminatorC(AckMsg, AM_ACKMSG);
  components CrcC;

  CogentHouseP.DisseminationControl -> DisseminationC;
  CogentHouseP.AckValue -> DisseminatorC;
  CogentHouseP.CRCCalc -> CrcC;


#ifdef SIP
  /************* SIP CONFIG ***********/
  //SIP Components
  components SIPControllerC, PredictC;
  components FilterM;
  components DEWMAC; 
  components PassThroughC as Pass;
  components new TimerMilliC() as HeartBeatTimer;
  components new HeartbeatC(HEARTBEAT_MULTIPLIER, HEARTBEAT_PERIOD);

  //Global SIP modules
  SIPControllerC.SinkStatePredict -> PredictC;
  HeartbeatC.HeartbeatTimer -> HeartBeatTimer;
  SIPControllerC.Heartbeat -> HeartbeatC;
  FilterM.LocalTime -> HilTimerMilliC;
  
  // Temp Wiring
  FilterM.Filter[RS_TEMPERATURE] -> DEWMAC.Filter[RS_TEMPERATURE];
  FilterM.GetSensorValue[RS_TEMPERATURE]  -> ThermalSensingM.ReadTemp;
  SIPControllerC.EstimateCurrentState[RS_TEMPERATURE]  -> FilterM.EstimateCurrentState[RS_TEMPERATURE];
  CogentHouseP.ReadTemp -> SIPControllerC.SIPController[RS_TEMPERATURE];

  // Hum Wiring
  FilterM.Filter[RS_HUMIDITY]  -> DEWMAC.Filter[RS_HUMIDITY];
  FilterM.GetSensorValue[RS_HUMIDITY]  -> ThermalSensingM.ReadHum;
  SIPControllerC.EstimateCurrentState[RS_HUMIDITY]  -> FilterM.EstimateCurrentState[RS_HUMIDITY];
  CogentHouseP.ReadHum -> SIPControllerC.SIPController[RS_HUMIDITY];

  // Battery Wiring
  FilterM.Filter[RS_VOLTAGE]  -> DEWMAC.Filter[RS_VOLTAGE];
  FilterM.GetSensorValue[RS_VOLTAGE]  -> BatterySensingM.ReadBattery;
  SIPControllerC.EstimateCurrentState[RS_VOLTAGE]  -> FilterM.EstimateCurrentState[RS_VOLTAGE];
  CogentHouseP.ReadVolt -> SIPControllerC.SIPController[RS_VOLTAGE];

  // CO2 Wiring
  FilterM.Filter[RS_CO2]  -> DEWMAC.Filter[RS_CO2];
  FilterM.GetSensorValue[RS_CO2]  -> AirQualityM.ReadCO2;
  SIPControllerC.EstimateCurrentState[RS_CO2]  -> FilterM.EstimateCurrentState[RS_CO2];
  CogentHouseP.ReadCO2 -> SIPControllerC.SIPController[RS_CO2];

  // AQ Wiring
  FilterM.Filter[RS_AQ]  -> DEWMAC.Filter[RS_AQ];
  FilterM.GetSensorValue[RS_AQ]  -> AirQualityM.ReadAQ;
  SIPControllerC.EstimateCurrentState[RS_AQ]  -> FilterM.EstimateCurrentState[RS_AQ] ;
  CogentHouseP.ReadAQ -> SIPControllerC.SIPController[RS_AQ] ;

  // VOC Wiring
  FilterM.Filter[RS_VOC]  -> DEWMAC.Filter[RS_VOC];
  FilterM.GetSensorValue[RS_VOC]  -> AirQualityM.ReadVOC;
  SIPControllerC.EstimateCurrentState[RS_VOC]  -> FilterM.EstimateCurrentState[RS_VOC] ;
  CogentHouseP.ReadVOC -> SIPControllerC.SIPController[RS_VOC] ;
  

  //Opti Smart Wiring
  CogentHouseP.OptiControl -> PulseReaderM.PulseControl;
  FilterM.Filter[RS_OPTI]  -> Pass.Filter[RS_OPTI];
  FilterM.GetSensorValue[RS_OPTI]  -> PulseReaderM.ReadPulse;
  SIPControllerC.EstimateCurrentState[RS_OPTI]  -> FilterM.EstimateCurrentState[RS_OPTI] ;
  CogentHouseP.ReadOpti -> SIPControllerC.SIPController[RS_OPTI] ;
  
  
  FilterM.Filter[RS_TEMPADC1]  -> DEWMAC.Filter[RS_TEMPADC1];
  FilterM.GetSensorValue[RS_TEMPADC1]  -> TempADCM.ReadTempADC1;
  SIPControllerC.EstimateCurrentState[RS_TEMPADC1]  -> FilterM.EstimateCurrentState[RS_TEMPADC1];
  CogentHouseP.ReadTempADC1 -> SIPControllerC.SIPController[RS_TEMPADC1];

  //Transmission Control
  CogentHouseP.TransmissionControl -> SIPControllerC.TransmissionControl;
#endif


#ifdef BN
  /************* BN CONFIG ***********/

  components new TimerMilliC() as HeartBeatTimer;
  components new HeartbeatC(HEARTBEAT_MULTIPLIER, HEARTBEAT_PERIOD);
  HeartbeatC.HeartbeatTimer -> HeartBeatTimer;
  CogentHouseP.Heartbeat -> HeartbeatC;
  
  // Temp Wiring
  components new ExposureControllerC(TEMP_BAND_LEN,BN_TEMP_BAND_THRESH) as TempBN;
  components new ExposureC(TEMP_BAND_LEN, RS_TEMPERATURE, BN_GAMMA) as TempExposure;

  TempExposure.GetValue -> ThermalSensingM.ReadTemp;
  TempBN.ExposureRead -> TempExposure.Read;
  CogentHouseP.ReadTemp -> TempBN.BNController;

  // Hum Wiring
  components new ExposureControllerC(HUM_BAND_LEN, BN_HUM_BAND_THRESH) as HumBN;
  components new ExposureC(HUM_BAND_LEN, RS_HUMIDITY, BN_GAMMA) as HumExposure;

  HumExposure.GetValue -> ThermalSensingM.ReadHum;
  HumBN.ExposureRead -> HumExposure.Read;
  CogentHouseP.ReadHum -> HumBN.BNController;

  // Battery Wiring
  components LowBatteryC;  
  LowBatteryC.BatteryRead -> BatterySensingM.ReadBattery;
  CogentHouseP.ReadVolt -> LowBatteryC.BNController;

  // CO2 Wiring
  components new ExposureControllerC(CO2_BAND_LEN,BN_CO2_BAND_THRESH) as CO2BN;
  components new ExposureC(CO2_BAND_LEN, RS_CO2, BN_GAMMA) as CO2Exposure;
  
  CO2Exposure.GetValue -> AirQualityM.ReadCO2;
  CO2BN.ExposureRead -> CO2Exposure.Read;
  CogentHouseP.ReadCO2 -> CO2BN.BNController;


  // AQ Wiring
  components new ExposureControllerC(AQ_BAND_LEN,BN_AQ_BAND_THRESH) as AQBN;
  components new ExposureC(AQ_BAND_LEN, RS_AQ, BN_GAMMA) as AQExposure;

  AQExposure.GetValue -> AirQualityM.ReadAQ;
  AQBN.ExposureRead -> AQExposure.Read;
  CogentHouseP.ReadAQ -> AQBN.BNController;


  // VOC Wiring
  components new ExposureControllerC(VOC_BAND_LEN, BN_VOC_BAND_THRESH) as VOCBN;
  components new ExposureC(VOC_BAND_LEN, RS_VOC, BN_GAMMA) as VOCExposure;

  VOCExposure.GetValue -> AirQualityM.ReadVOC;
  VOCBN.ExposureRead -> VOCExposure.Read;
  CogentHouseP.ReadVOC -> VOCBN.BNController;
#endif

}
