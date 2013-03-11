// -*- c -*-
#include "msp430usart.h"
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
configuration ClampTestC { }

implementation
{
  components MainC, ClampTestP, ClampM, LedsC;
  components new TimerMilliC() as SensingTimer;
  components new TimerMilliC() as ClampTimer;
  components HilTimerMilliC;
  components PrintfC, SerialStartC;
  components new ClampC() as Clamp;
  
  ClampM.SenseTimer->ClampTimer;
  ClampM.GetClamp -> Clamp;  
  
  ClampTestP.Boot -> MainC.Boot;
  ClampTestP.LocalTime -> HilTimerMilliC;
  ClampTestP.ReadClamp->ClampM.ReadClamp;
  ClampTestP.ClampControl -> ClampM.ClampControl;
  ClampTestP.SensingTimer ->SensingTimer; 
}

