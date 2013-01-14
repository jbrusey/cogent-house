// -*- c -*-
#include "printf.h"
#include "minunit.h"

configuration TestFloatApp { }

implementation
{


  components MainC, TestFloatP, HilTimerMilliC;
  components PrintfC, SerialStartC;
  TestFloatP.Boot -> MainC.Boot;
  TestFloatP.LocalTime -> HilTimerMilliC;

  
}

