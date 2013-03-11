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
  
  components DEWMAC as DEWMASine;

  components PrintfC;
  components SerialStartC;
  components RandomC;
  components LedsC;

  DEWMATestP.Boot -> MainC.Boot; 
  DEWMATestP.Random -> RandomC;
  DEWMATestP.Leds -> LedsC;

  DEWMATestP.DEWMASine -> DEWMASine.Filter[1];
}

