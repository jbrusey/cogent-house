// -*- c -*-
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#include "minunit.h"
#include <stdint.h>

configuration PredictTestC {}

implementation
{
  components MainC, PredictTestP;
  
  components PrintfC;
  components SerialStartC;
  components RandomC;
  components LedsC;
  components PredictC;


  PredictTestP.Boot -> MainC.Boot; 
  PredictTestP.Random -> RandomC;
  PredictTestP.Leds -> LedsC;
  PredictTestP.Predict -> PredictC;

}

