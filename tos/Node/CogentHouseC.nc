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
  components CogentHouseP, ActiveMessageC, MainC, LedsC, ActiveMessageC as Radio;
#ifdef DEBUG
  components PrintfC;
  components SerialStartC;
#endif
	
  //import timers
  components new TimerMilliC() as SenseTimer;
  components new TimerMilliC() as SendTimeoutTimer;
  components new TimerMilliC() as BlinkTimer;
  components new TimerMilliC() as WarmUpTimer;   
  components new TimerMilliC() as TimeOut;

  CogentHouseP.Boot -> MainC.Boot;
  CogentHouseP.SenseTimer -> SenseTimer;
  CogentHouseP.SendTimeoutTimer -> SendTimeoutTimer;
  CogentHouseP.BlinkTimer -> BlinkTimer;
  CogentHouseP.Leds -> LedsC;
  CogentHouseP.RadioControl -> ActiveMessageC;
  CogentHouseP.LowPowerListening -> Radio;

  //sensing interfaces
  components new SensirionSht11C();
  components new HamamatsuS1087ParC() as PAR;
  components new HamamatsuS10871TsrC() as TSR;
  components new VoltageC() as Volt;
  components new CarbonDioxideC() as CarbonDioxide;
  components new VOCC() as VOC;
  components new AQC() as AQ;
  components HplMsp430InterruptP as GIOInterrupt;
  components HplMsp430GeneralIOC as GIO;
  components new Temp_ADC1C() as Temp_ADC1;
  components new Temp_ADC2C() as Temp_ADC2;
  components new BlackBulbC() as BlackBulbADC;

  //import sensing modules
  components ThermalSensingM;
  components LightSensingM;
  components AirQualityM;
  components WindowSensorM;
  components HeatMeterM;
  components new PulseReaderM() as OptiReader;
  components BlackBulbM;

  //sensor readings
  ThermalSensingM.GetTemp -> SensirionSht11C.Temperature;
  ThermalSensingM.GetHum ->SensirionSht11C.Humidity;

  OptiReader.Leds -> LedsC;
  OptiReader.EnergyInput -> GIO.Port26;
  OptiReader.EnergyInterrupt -> GIOInterrupt.Port26; //set to read from gio3

  LightSensingM.GetPAR -> PAR;
  LightSensingM.GetTSR -> TSR;

  WindowSensorM.GetTempADC1 -> Temp_ADC1;
  WindowSensorM.GetTempADC2 -> Temp_ADC2;
  BlackBulbM.GetTemp -> BlackBulbADC;
  
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
  CogentHouseP.ReadPAR->LightSensingM.ReadPAR;
  CogentHouseP.ReadTSR->LightSensingM.ReadTSR;
  CogentHouseP.ReadVolt->Volt;
  CogentHouseP.ReadCO2->AirQualityM.ReadCO2;
  CogentHouseP.ReadVOC->AirQualityM.ReadVOC;
  CogentHouseP.ReadAQ->AirQualityM.ReadAQ;
  CogentHouseP.ReadOpti->OptiReader.ReadPulse;
  CogentHouseP.OptiControl -> OptiReader.PulseControl;
  CogentHouseP.ReadTempADC1->WindowSensorM.ReadTempADC1;
  CogentHouseP.ReadTempADC2->WindowSensorM.ReadTempADC2;
  CogentHouseP.ReadBlackBulb->BlackBulbM.ReadTemp;

  CogentHouseP.ReadHeatMeter->HeatMeterM.ReadHeatMeter;
  CogentHouseP.HeatMeterControl -> HeatMeterM.HeatMeterControl;

  // Instantiate and wire our collection service
  components CollectionC;
  components new CollectionSenderC(AM_STATEMSG) as StateSender;
  components HilTimerMilliC;

  CogentHouseP.CollectionControl -> CollectionC;
  CogentHouseP.CtpInfo -> CollectionC;
  CogentHouseP.StateSender -> StateSender;
	
  CogentHouseP.LocalTime -> HilTimerMilliC;

#ifdef DISSEMINATE
  // Instantiate and wire the settings dissemination service 
  components DisseminationC;
  CogentHouseP.DisseminationControl -> DisseminationC;
	
  components new DisseminatorC(ConfigMsg, DIS_SETTINGS);
  CogentHouseP.SettingsValue -> DisseminatorC;
#endif

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

  //components new LogStorageC(VOLUME_DEBUGLOG, TRUE);
  //CogentHouseP.DebugLog -> LogStorageC;
}
