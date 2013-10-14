// -*- c -*-
#include "Packets.h"
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
  CogentHouseP.SendTimeOutTimer -> SendTimeOutTimer;

  // Instantiate and wire our collection service
  components CollectionC, ActiveMessageC;
  components new CollectionSenderC(AM_STATEMSG) as StateSender;

  CogentHouseP.RadioControl -> ActiveMessageC;
  CogentHouseP.CollectionControl -> CollectionC;
  CogentHouseP.CtpInfo -> CollectionC;
  CogentHouseP.StateSender -> StateSender;


  /*********** ACK CONFIG *************/

  components DisseminationC;
  components new DisseminatorC(AckMsg, AM_ACKMSG);
  components CrcC;

  CogentHouseP.DisseminationControl -> DisseminationC;
  CogentHouseP.AckValue -> DisseminatorC;
  CogentHouseP.CRCCalc -> CrcC;

  
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


  //Sensing Modules
  components ThermalSensingM, AirQualityM, BatterySensingM, HeatMeterM, OptiSmartM;

  //Wire up Sensing
  ThermalSensingM.GetTemp -> SensirionSht11C.Temperature;
  ThermalSensingM.GetHum ->SensirionSht11C.Humidity;
  BatterySensingM.GetVoltage -> Volt;
  OptiSmartM.Leds -> LedsC;
  OptiSmartM.EnergyInput -> GIO.Port26;
  OptiSmartM.EnergyInterrupt -> GIOInterrupt.Port26; //set to read from gio3
  AirQualityM.GetCO2 -> CarbonDioxide;
  AirQualityM.GetVOC -> VOC;
  AirQualityM.GetAQ -> AQ;
  AirQualityM.CO2On -> GIO.Port23; //set to gio2
  AirQualityM.WarmUpTimer -> WarmUpTimer;

  HeatMeterM.EnergyInput -> GIO.Port26;
  HeatMeterM.EnergyInterrupt -> GIOInterrupt.Port26; //set to read from gio3
  HeatMeterM.VolumeInput -> GIO.Port23;
  HeatMeterM.VolumeInterrupt -> GIOInterrupt.Port23; //set to read from gio2

  //link modules to main file
  CogentHouseP.ReadTemp->ThermalSensingM.ReadTemp;
  CogentHouseP.ReadHum->ThermalSensingM.ReadHum;
  CogentHouseP.ReadBattery->BatterySensingM.ReadBattery;
  CogentHouseP.ReadCO2->AirQualityM.ReadCO2;
  CogentHouseP.ReadVOC->AirQualityM.ReadVOC;
  CogentHouseP.ReadAQ->AirQualityM.ReadAQ;
  CogentHouseP.ReadOpti->OptiSmartM.ReadOpti;
  CogentHouseP.OptiControl -> OptiSmartM.OptiControl;

  CogentHouseP.ReadHeatMeter->HeatMeterM.ReadHeatMeter;
  CogentHouseP.HeatMeterControl -> HeatMeterM.HeatMeterControl;

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
}
