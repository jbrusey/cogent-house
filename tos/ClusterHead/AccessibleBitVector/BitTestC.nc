// -*- c -*-
/* #include "msp430usart.h" */
#include "minunit.h"
#define NEW_PRINTF_SEMANTICS
#include "printf.h"

configuration BitTestC { }

implementation
{
  components MainC, BitTestP;
  components PrintfC;
  components SerialStartC;

  components new AccessibleBitVectorC(10);
  BitTestP.Bs -> AccessibleBitVectorC.AccessibleBitVector;
  BitTestP.Boot -> MainC.Boot; 
}

