// -*- c -*-
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#include "Filter.h"
#include "Packets.h"

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
  ControllerTestP.TEMPSIPRead -> SIPControllerC.Sensor[0];

  // Hum Wiring
  FilterM.Filter[1] -> DEWMA.Filter[1];
  FilterM.GetSensorValue[1] -> ThermalSensingM.ReadHum;
  SIPControllerC.EstimateCurrentState[1] -> FilterM.EstimateCurrentState[1];
  ControllerTestP.HUMSIPRead -> SIPControllerC.Sensor[1];

  //Transmission Control
  ControllerTestP.TransmissionControl -> SIPControllerC.TransmissionControl;


}

