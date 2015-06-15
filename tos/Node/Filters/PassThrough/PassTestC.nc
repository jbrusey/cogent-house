// -*- c -*-
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#include "minunit.h"
#include <stdint.h>

configuration PassTestC {}

implementation
{
  components MainC, PassTestP;
  
  components PassThroughC as Pass;

  components PrintfC;
  components SerialStartC;
  components RandomC;
  components LedsC;

  PassTestP.Boot -> MainC.Boot; 
  PassTestP.Random -> RandomC;
  PassTestP.Leds -> LedsC;

  PassTestP.Pass -> Pass.Filter[1];
}

