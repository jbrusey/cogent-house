// -*- c -*-
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#include "minunit.h"
#include <stdint.h>

#define HIGH_COVARIANCE 1e20

configuration DEWMATestC {}

implementation
{
  components MainC, DEWMATestP;
  
  components new DEWMAC(10., 1/64., TRUE, 0.1, 0.1) as DEWMASine;

  components PrintfC;
  components SerialStartC;
  components RandomC;
  components LedsC;

  DEWMATestP.Boot -> MainC.Boot; 
  DEWMATestP.Random -> RandomC;
  DEWMATestP.Leds -> LedsC;

  DEWMATestP.DEWMASine -> DEWMASine;
}

