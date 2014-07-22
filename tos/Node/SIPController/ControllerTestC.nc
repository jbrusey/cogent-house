// -*- c -*-
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#include "../Sensing/PolyClass/horner.c"
#include "Filter.h"

enum {
  RS_SIZE = 4,
};


configuration ControllerTestC {}

implementation
{
  components MainC, ControllerTestP;
  components new TimerMilliC() as SenseTimer;
  components HilTimerMilliC;  
  components new BitVectorC(RS_SIZE) as ExpectReadDone;
  
  components PrintfC;
  components SerialStartC;

  components LedsC;


  //Hearbeat
  components new TimerMilliC() as HeartBeatTimer;
  components new HeartbeatC(10, 307200);

  components PredictC;


  //Sensors
  components new SensirionSht11C();
  components PulseGio2C;

  //Sensing Modules
  components ThermalSensingM;


  //SIP Components
  components SIPControllerC;
  components DEWMAC as DEWMA; //Filter
  components PassThroughC as Pass;
  components FilterM;


  //Main Section
  ControllerTestP.Boot -> MainC.Boot; 
  ControllerTestP.Leds -> LedsC;
  ControllerTestP.SenseTimer -> SenseTimer;
  ControllerTestP.ExpectReadDone -> ExpectReadDone;

  //Wire up Sensing
  ThermalSensingM.GetTemp -> SensirionSht11C.Temperature;
  ThermalSensingM.GetHum ->SensirionSht11C.Humidity;

  //Global SIP modules
  SIPControllerC.SinkStatePredict -> PredictC;
  HeartbeatC.HeartbeatTimer -> HeartBeatTimer;
  SIPControllerC.Heartbeat -> HeartbeatC;

  
  // Temp Wiring
  FilterM.Filter[0] -> DEWMA.Filter[0];
  FilterM.GetSensorValue[0] -> ThermalSensingM.ReadTemp;
  FilterM.LocalTime -> HilTimerMilliC;
  SIPControllerC.EstimateCurrentState[0] -> FilterM.EstimateCurrentState[0];
  ControllerTestP.TEMPSIPRead -> SIPControllerC.SIPController[0];

  // Hum Wiring
  FilterM.Filter[1] -> DEWMA.Filter[1];
  FilterM.GetSensorValue[1] -> ThermalSensingM.ReadHum;
  SIPControllerC.EstimateCurrentState[1] -> FilterM.EstimateCurrentState[1];
  ControllerTestP.HUMSIPRead -> SIPControllerC.SIPController[1];

  //Heat meter energy Wiring
  FilterM.Filter[2]  -> Pass.Filter[2];
  FilterM.GetSensorValue[2]  -> PulseGio2C.ReadPulse;
  SIPControllerC.EstimateCurrentState[2]  -> FilterM.EstimateCurrentState[2] ;
  ControllerTestP.HMEnergyControl -> PulseGio2C.PulseControl;
  ControllerTestP.ReadHMEnergy -> SIPControllerC.SIPController[2] ;

  //Opti smart
  FilterM.Filter[3]  -> Pass.Filter[3];
  FilterM.GetSensorValue[3]  -> PulseGio2C.ReadPulse;
  SIPControllerC.EstimateCurrentState[3]  -> FilterM.EstimateCurrentState[3] ;
  ControllerTestP.OptiControl -> PulseGio2C.PulseControl;
  ControllerTestP.ReadOpti -> SIPControllerC.SIPController[3] ;

  //Transmission Control
  ControllerTestP.TransmissionControl -> SIPControllerC.TransmissionControl;


}

