// -*- c -*-
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#include "minunit.h"

configuration ExposureEventDetectorTestC {}

implementation
{
  //const float Thresh = 3.;
  components MainC,ExposureEventDetectorTestP;
  components new ExposureEventDetectorC(5,10.) as ED;
  components PrintfC;
  components SerialStartC;
  components DemoFilterM;

  ED.ExposureRead -> DemoFilterM.Read;
  ExposureEventDetectorTestP.EventRead -> ED.Read;
  ExposureEventDetectorTestP.Boot -> MainC.Boot; 
  ExposureEventDetectorTestP.TransmissionControl -> ED;
}

