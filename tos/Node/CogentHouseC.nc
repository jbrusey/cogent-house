// -*- c -*-
#include "../Packets.h"
#include "Collection.h"
#include "./Sensing/PolyClass/horner.c"
#include "Filter.h"
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

  components CrcC;
  CogentHouseP.CRCCalc -> CrcC;

  PackState.Mask -> ABV;
  CogentHouseP.PackState -> PackState;

  //sensing interfaces
  components new SensirionSht11C();
  components new VoltageC() as Volt; 
  components new Temp_ADC0C() as Temp_ADC0;
  components new Temp_ADC1C() as Temp_ADC1;
  components new Temp_ADC2C() as Temp_ADC2;
  components new Temp_ADC3C() as Temp_ADC3;
  components new Flow_ADC1C() as Flow_ADC1;
  components new Flow_ADC3C() as Flow_ADC3;
  components new Flow_ADC7C() as Flow_ADC7;
  components new SolarC() as Solar;
  components new Solar_ADC3C() as Solar_ADC3;
  components new BlackBulbC() as BlackBulb;
  components new CarbonDioxideC() as CarbonDioxide;
  components HplMsp430InterruptP as GIOInterrupt;
  components HplMsp430GeneralIOC as GIO;

  //Sensing Modules
  components ThermalSensingM, BatterySensingM, CarM;

  //Wire up Sensing
  ThermalSensingM.GetTemp -> SensirionSht11C.Temperature;
  ThermalSensingM.GetHum ->SensirionSht11C.Humidity;
  BatterySensingM.GetVoltage -> Volt;
  
  CarM.GetTempADC0 -> Temp_ADC0;
  CarM.GetTempADC1 -> Temp_ADC1;
  CarM.GetTempADC2 -> Temp_ADC2;
  CarM.GetTempADC3 -> Temp_ADC3;
  CarM.GetFlowADC1 -> Flow_ADC1;
  CarM.GetFlowADC3 -> Flow_ADC3;
  CarM.GetFlowADC7 -> Flow_ADC7;
  CarM.GetSolar -> Solar;
  CarM.GetSolar_ADC3 -> Solar_ADC3;
  CarM.GetBlackBulb -> BlackBulb;
  CarM.GetCO2 -> CarbonDioxide;
  CarM.CO2On -> GIO.Port23; //set to gio2
  CarM.WarmUpTimer -> WarmUpTimer;
  
  /*********** ACK CONFIG *************/

  // ack interfaces
  components new AMReceiverC(AM_ACKMSG) as AckReceiver;
  CogentHouseP.AckReceiver -> AckReceiver;


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
  FilterM.GetSensorValue[RS_CO2]  -> CarM.ReadCO2;
  SIPControllerC.EstimateCurrentState[RS_CO2]  -> FilterM.EstimateCurrentState[RS_CO2];
  CogentHouseP.ReadCO2 -> SIPControllerC.SIPController[RS_CO2];
  
  FilterM.Filter[RS_TEMPADC0]  -> DEWMAC.Filter[RS_TEMPADC0];
  FilterM.GetSensorValue[RS_TEMPADC0]  -> CarM.ReadTempADC0;
  SIPControllerC.EstimateCurrentState[RS_TEMPADC0]  -> FilterM.EstimateCurrentState[RS_TEMPADC0];
  CogentHouseP.ReadTempADC0 -> SIPControllerC.SIPController[RS_TEMPADC0];
  
  FilterM.Filter[RS_TEMPADC1]  -> DEWMAC.Filter[RS_TEMPADC1];
  FilterM.GetSensorValue[RS_TEMPADC1]  -> CarM.ReadTempADC1;
  SIPControllerC.EstimateCurrentState[RS_TEMPADC1]  -> FilterM.EstimateCurrentState[RS_TEMPADC1];
  CogentHouseP.ReadTempADC1 -> SIPControllerC.SIPController[RS_TEMPADC1];
  
  FilterM.Filter[RS_TEMPADC2]  -> DEWMAC.Filter[RS_TEMPADC2];
  FilterM.GetSensorValue[RS_TEMPADC2]  -> CarM.ReadTempADC2;
  SIPControllerC.EstimateCurrentState[RS_TEMPADC2]  -> FilterM.EstimateCurrentState[RS_TEMPADC2];
  CogentHouseP.ReadTempADC2 -> SIPControllerC.SIPController[RS_TEMPADC2];
  
  FilterM.Filter[RS_TEMPADC3]  -> DEWMAC.Filter[RS_TEMPADC3];
  FilterM.GetSensorValue[RS_TEMPADC3]  -> CarM.ReadTempADC3;
  SIPControllerC.EstimateCurrentState[RS_TEMPADC3]  -> FilterM.EstimateCurrentState[RS_TEMPADC3];
  CogentHouseP.ReadTempADC3 -> SIPControllerC.SIPController[RS_TEMPADC3];
  
  FilterM.Filter[RS_FLOWADC1]  -> DEWMAC.Filter[RS_FLOWADC1];
  FilterM.GetSensorValue[RS_FLOWADC1]  -> CarM.ReadFlowADC1;
  SIPControllerC.EstimateCurrentState[RS_FLOWADC1]  -> FilterM.EstimateCurrentState[RS_FLOWADC1];
  CogentHouseP.ReadFlowADC1 -> SIPControllerC.SIPController[RS_FLOWADC1];
  
  FilterM.Filter[RS_FLOWADC3]  -> DEWMAC.Filter[RS_FLOWADC3];
  FilterM.GetSensorValue[RS_FLOWADC3]  -> CarM.ReadFlowADC3;
  SIPControllerC.EstimateCurrentState[RS_FLOWADC3]  -> FilterM.EstimateCurrentState[RS_FLOWADC3];
  CogentHouseP.ReadFlowADC3 -> SIPControllerC.SIPController[RS_FLOWADC3];
  
  FilterM.Filter[RS_FLOWADC7]  -> DEWMAC.Filter[RS_FLOWADC7];
  FilterM.GetSensorValue[RS_FLOWADC7]  -> CarM.ReadFlowADC7;
  SIPControllerC.EstimateCurrentState[RS_FLOWADC7]  -> FilterM.EstimateCurrentState[RS_FLOWADC7];
  CogentHouseP.ReadFlowADC7 -> SIPControllerC.SIPController[RS_FLOWADC7];
  
  FilterM.Filter[RS_SOLAR]  -> DEWMAC.Filter[RS_SOLAR];
  FilterM.GetSensorValue[RS_SOLAR]  -> CarM.ReadSolar;
  SIPControllerC.EstimateCurrentState[RS_SOLAR]  -> FilterM.EstimateCurrentState[RS_SOLAR];
  CogentHouseP.ReadSolar -> SIPControllerC.SIPController[RS_SOLAR];
  
  FilterM.Filter[RS_SOLARADC3]  -> DEWMAC.Filter[RS_SOLARADC3];
  FilterM.GetSensorValue[RS_SOLARADC3]  -> CarM.ReadSolar_ADC3;
  SIPControllerC.EstimateCurrentState[RS_SOLARADC3]  -> FilterM.EstimateCurrentState[RS_SOLARADC3];
  CogentHouseP.ReadSolarADC3 -> SIPControllerC.SIPController[RS_SOLARADC3];
  
  FilterM.Filter[RS_BLACKBULB]  -> DEWMAC.Filter[RS_BLACKBULB];
  FilterM.GetSensorValue[RS_BLACKBULB]  -> CarM.ReadBlackBulb;
  SIPControllerC.EstimateCurrentState[RS_BLACKBULB]  -> FilterM.EstimateCurrentState[RS_BLACKBULB];
  CogentHouseP.ReadBlackBulb -> SIPControllerC.SIPController[RS_BLACKBULB];
  
  //Transmission Control
  CogentHouseP.TransmissionControl -> SIPControllerC.TransmissionControl;
}
