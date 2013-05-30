// -*- c -*-
#define NEW_PRINTF_SEMANTICS
#include "printf.h"


configuration ExposureEventDetectorTestC {}

implementation
{
  //const float Thresh = 3.;
  components MainC,ExposureEventDetectorTestP;
  components new ExposureControllerC(5, 10.) as ED;
  components SerialStartC;
  components DemoFilterM;
  components PrintfC;


  ED.ExposureRead -> DemoFilterM.Read;
  ExposureEventDetectorTestP.EventRead -> ED;
  ExposureEventDetectorTestP.Boot -> MainC.Boot; 
}

