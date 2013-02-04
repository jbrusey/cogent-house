// -*- c -*-
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#include "minunit.h"

configuration EventDetectorTestC {}

implementation
{
  //const float Thresh = 3.;
  components MainC,EventDetectorTestP;
  components EventDetectorC as ED;
  components PrintfC;
  components SerialStartC;
  components DemoFilterM;
  components DemoPredictM;

  ED.FilterRead[0] -> DemoFilterM.Read;
  ED.ValuePredict[0] -> DemoPredictM;
  EventDetectorTestP.EventRead -> ED.Read[0];
  EventDetectorTestP.Boot -> MainC.Boot; 
  EventDetectorTestP.TransmissionControl -> ED.TransmissionControl[0];
}

