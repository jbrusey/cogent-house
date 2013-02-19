// -*- c -*-
#include "../Packets.h"
#include "Collection.h"
#include "PolyClass/horner.c"
#include "CurrentCost/cc_struct.h"
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

  // Instantiate and wire our collection service
  components CollectionC, ActiveMessageC;
  components new CollectionSenderC(AM_STATEMSG) as StateSender;

  CogentHouseP.RadioControl -> ActiveMessageC;
  CogentHouseP.CollectionControl -> CollectionC;
  CogentHouseP.CtpInfo -> CollectionC;
  CogentHouseP.StateSender -> StateSender;
  
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



  /************* SENSING CONFIG ***********/

  components new SensirionSht11C();
  components new HamamatsuS1087ParC() as PAR;
  components new HamamatsuS10871TsrC() as TSR;
  components new VoltageC() as Volt;
  components new CarbonDioxideC() as CarbonDioxide;
  components new VOCC() as VOC;
  components new AQC() as AQ;
  components HplMsp430InterruptP as GIOInterrupt;
  components HplMsp430GeneralIOC as GIO;

  //Sensing Modules
  components ThermalSensingM, AirQualityM, BatterySensingM, LightSensingM;;

  //Wire up Sensing
  ThermalSensingM.GetTemp -> SensirionSht11C.Temperature;
  ThermalSensingM.GetHum ->SensirionSht11C.Humidity;
  LightSensingM.GetPAR -> PAR;
  LightSensingM.GetTSR -> TSR;
  BatterySensingM.GetVoltage -> Volt;
  AirQualityM.GetCO2 -> CarbonDioxide;
  AirQualityM.GetVOC -> VOC;
  AirQualityM.GetAQ -> AQ;
  AirQualityM.CO2On -> GIO.Port23; //set to gio2
  AirQualityM.WarmUpTimer -> WarmUpTimer;

  /*********** ACK CONFIG *************/

  // ack interfaces
  components new AMReceiverC(AM_ACKMSG) as AckReceiver;
  components new AMSenderC(AM_ACKMSG) as AckForwarder;
  components new HashMapC(HASH_SIZE) as AckHeardMap;
  components new QueueC(AckMsg_t*, RADIO_QUEUE_SIZE) as AckQueue;
  components new PoolC(message_t, RADIO_QUEUE_SIZE) as AckPool;
  components CrcC;

  CogentHouseP.AckReceiver -> AckReceiver;
  CogentHouseP.AckForwarder -> AckForwarder;
  CogentHouseP.Packet -> AckForwarder;
  CogentHouseP.AckHeardMap -> AckHeardMap;
  CogentHouseP.AckQueue -> AckQueue;
  CogentHouseP.AckPool -> AckPool;
  CogentHouseP.CRCCalc -> CrcC;

  //link modules to main file
  CogentHouseP.ReadTemp->ThermalSensingM.ReadTemp;
  CogentHouseP.ReadHum->ThermalSensingM.ReadHum;
  CogentHouseP.ReadPAR->LightSensingM.ReadPAR;
  CogentHouseP.ReadTSR->LightSensingM.ReadTSR;
  CogentHouseP.ReadVolt->BatterySensingM.ReadBattery;
  CogentHouseP.ReadCO2->AirQualityM.ReadCO2;
  CogentHouseP.ReadVOC->AirQualityM.ReadVOC;
  CogentHouseP.ReadAQ->AirQualityM.ReadAQ;
	
}
