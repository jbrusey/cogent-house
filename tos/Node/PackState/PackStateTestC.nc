// -*- c -*-
#include "msp430usart.h"

enum {
  SC_SIZE = 20,
  SC_PACKED_SIZE = 5
};

#include "packstate.h" 
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#include "minunit.h"


configuration PackStateTestC { }

implementation
{
  components MainC, PackStateTestP;
  components new PackStateC(SC_SIZE) as PackState;
  components new AccessibleBitVectorC(SC_SIZE) as ABV;

  components PrintfC;
  components SerialStartC;
  components LedsC;


  PackStateTestP.Boot -> MainC.Boot; 
  PackState.Mask -> ABV;
  PackStateTestP.PackState -> PackState;
  PackStateTestP.Leds -> LedsC;
}

