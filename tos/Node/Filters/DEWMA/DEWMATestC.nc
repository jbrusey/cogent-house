// -*- c -*-
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#include "minunit.h"
#include "SIPController.h"
#include <stdint.h>

configuration DEWMATestC {}

implementation
{
  components MainC, DEWMATestP;
  
  components DEWMAC as Dewma;

  components PrintfC;
  components SerialStartC;
  components RandomC;
  components LedsC;
  components PredictC;

  DEWMATestP.Boot -> MainC.Boot; 
  DEWMATestP.Random -> RandomC;
  DEWMATestP.Leds -> LedsC;

  DEWMATestP.Dewma -> Dewma.Filter[1];
  DEWMATestP.Predict -> PredictC;
}

