// -*- c -*-
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#include "minunit.h"

configuration EventDetectorTestC {}

implementation
{
  //const float Thresh = 3.;
  components MainC,EventDetectorTestP;
  components new EventDetectorC(9.) as ED;
  components PrintfC;
  components SerialStartC;
  components DemoFilterM;
  components DemoPredictM;

  ED.FilterRead -> DemoFilterM.Read;
  ED.ValuePredict -> DemoPredictM;
  EventDetectorTestP.EventRead -> ED.Read;
  EventDetectorTestP.Boot -> MainC.Boot; 
  EventDetectorTestP.TransmissionControl -> ED;
}

