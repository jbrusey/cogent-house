// -*- c -*-
#include "../Packets.h"
#include "Collection.h"
#include "PolyClass/horner.c"
#include "CurrentCost/cc_struct.h"
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
  components new TimerMilliC() as BlinkTimer;
  components new TimerMilliC() as WarmUpTimer;
  components new TimerMilliC() as SendTimeOutTimer;
  
  components RandomC;


  CogentHouseP.Boot -> MainC.Boot;
  CogentHouseP.SenseTimer -> SenseTimer;
  CogentHouseP.BlinkTimer -> BlinkTimer;
  CogentHouseP.SendTimeOutTimer -> SendTimeOutTimer;
  CogentHouseP.Leds -> LedsC;
  CogentHouseP.RadioControl -> ActiveMessageC;


  // Instantiate and wire our collection service
  components CollectionC;
  components new CollectionSenderC(AM_BNMSG) as StateSender;

  CogentHouseP.CollectionControl -> CollectionC;
  CogentHouseP.CtpInfo -> CollectionC;
  CogentHouseP.StateSender -> StateSender;

  // ack interfaces
  components new AMReceiverC(AM_ACKMSG) as AckReceiver;
  CogentHouseP.AckReceiver -> AckReceiver;
  components new AMSenderC(AM_ACKMSG) as AckForwarder;
  CogentHouseP.AckForwarder -> AckForwarder;
  CogentHouseP.Packet -> AckForwarder;

  components new HashMapC(HASH_SIZE) as AckHeardMap;
  CogentHouseP.AckHeardMap -> AckHeardMap;

  components new QueueC(AckMsg_t*, RADIO_QUEUE_SIZE) as AckQueue;
  components new PoolC(message_t, RADIO_QUEUE_SIZE) as AckPool;
  CogentHouseP.AckQueue -> AckQueue;
  CogentHouseP.AckPool -> AckPool;


  components CrcC;
  CogentHouseP.CRCCalc -> CrcC;

  //sensing interfaces
  components new SensirionSht11C();
  components new VoltageC() as Volt;
  components new CarbonDioxideC() as CarbonDioxide;
  components new VOCC() as VOC;
  components new AQC() as AQ;
  components HplMsp430InterruptP as GIOInterrupt;
  components HplMsp430GeneralIOC as GIO;

  //import sensing modules
  components ThermalSensingM;
  components AirQualityM;
  components BatterySensingM;

  //sensor readings
  ThermalSensingM.GetTemp -> SensirionSht11C.Temperature;
  ThermalSensingM.GetHum ->SensirionSht11C.Humidity;
  BatterySensingM.GetVoltage -> Volt;
  AirQualityM.GetCO2 -> CarbonDioxide;
  AirQualityM.GetVOC -> VOC;
  AirQualityM.GetAQ -> AQ;
  AirQualityM.CO2On -> GIO.Port23; //set to gio2
  AirQualityM.WarmUpTimer -> WarmUpTimer;

 
  //Temp
  components new ExposureEventDetectorC(TEMP_BAND_LEN,BN_TEMP_BAND_THRESH) as TempDetector;
  components new ExposureC(TEMP_BAND_LEN, RS_TEMPERATURE, BN_GAMMA) as TempExposure;
  
  TempExposure.GetValue -> ThermalSensingM.ReadTemp;
  TempDetector.ExposureRead -> TempExposure.Read;
  CogentHouseP.ReadTemp -> TempDetector.Read;
  CogentHouseP.TempTrans -> TempDetector.TransmissionControl;

  //Hum
  components new ExposureEventDetectorC(HUM_BAND_LEN,BN_HUM_BAND_THRESH) as HumDetector;
  components new ExposureC(HUM_BAND_LEN, RS_HUMIDITY, BN_GAMMA) as HumExposure;
  
  HumExposure.GetValue -> ThermalSensingM.ReadHum;
  HumDetector.ExposureRead -> HumExposure.Read;
  CogentHouseP.ReadHum -> HumDetector.Read;
  CogentHouseP.HumTrans -> HumDetector.TransmissionControl;

  //CO2
  components new ExposureEventDetectorC(CO2_BAND_LEN,BN_CO2_BAND_THRESH) as CO2Detector;
  components new ExposureC(CO2_BAND_LEN, RS_CO2, BN_GAMMA) as CO2Exposure;
  
  CO2Exposure.GetValue -> AirQualityM.ReadCO2;
  CO2Detector.ExposureRead -> CO2Exposure.Read;

  CogentHouseP.ReadCO2 -> CO2Detector.Read;
  CogentHouseP.CO2Trans -> CO2Detector.TransmissionControl;

  //VOC
  components new ExposureEventDetectorC(VOC_BAND_LEN,BN_VOC_BAND_THRESH) as VOCDetector;
  components new ExposureC(VOC_BAND_LEN, RS_VOC, BN_GAMMA) as VOCExposure;
  VOCExposure.GetValue -> AirQualityM.ReadVOC;
  VOCDetector.ExposureRead -> VOCExposure.Read;

  CogentHouseP.ReadVOC -> VOCDetector.Read;
  CogentHouseP.VOCTrans -> VOCDetector.TransmissionControl;


  //AQ
  components new ExposureEventDetectorC(AQ_BAND_LEN,BN_AQ_BAND_THRESH) as AQDetector;
  components new ExposureC(AQ_BAND_LEN, RS_AQ, BN_GAMMA) as AQExposure;
  AQExposure.GetValue -> AirQualityM.ReadAQ;
  AQDetector.ExposureRead -> AQExposure.Read;

  CogentHouseP.ReadAQ -> AQDetector.Read;
  CogentHouseP.AQTrans -> AQDetector.TransmissionControl;

  BatterySensingM.GetVoltage -> Volt;
  CogentHouseP.ReadVolt->BatterySensingM.ReadBattery;

  components HilTimerMilliC;
	
  CogentHouseP.LocalTime -> HilTimerMilliC;
  
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
