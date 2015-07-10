// -*- c -*-
#include "msp430usart.h"
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#include "printfloat.h"

configuration GIOSwitchTestC { }

implementation
{

  components MainC, GIOSwitchTestP;

  components new TimerMilliC() as Timer;
  components HilTimerMilliC;
  components PrintfC, SerialStartC;

  components SwitchGio2C;

  GIOSwitchTestP.Boot -> MainC.Boot;
  GIOSwitchTestP.LocalTime -> HilTimerMilliC;
  GIOSwitchTestP.SwitchControl -> SwitchGio2C.SwitchControl;
  GIOSwitchTestP.Timer ->Timer; 
}

