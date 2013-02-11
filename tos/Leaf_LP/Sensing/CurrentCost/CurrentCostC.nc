// -*- c -*-
#include "msp430usart.h"
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
configuration CurrentCostC { }

implementation
{
  components MainC, CurrentCostP, CurrentCostM,CurrentCostSerialC;
  components new TimerMilliC() as SensingTimer;
  components new TimerMilliC() as TimeoutTimer;
  components new TimerMilliC() as ResumeTimer;
  components new TimerMilliC() as FirstByteTimer;
  components HilTimerMilliC;
  components PrintfC, SerialStartC;

  CurrentCostP.Boot -> MainC.Boot;
  
  CurrentCostM.CurrentCostUartStream -> CurrentCostSerialC;
  CurrentCostM.UartControl -> CurrentCostSerialC;
  CurrentCostM.TimeoutTimer -> TimeoutTimer;
  CurrentCostM.ResumeTimer -> ResumeTimer;
  CurrentCostM.FirstByteTimer -> FirstByteTimer;
  CurrentCostM.LocalTime -> HilTimerMilliC;

  CurrentCostP.ReadWattage->CurrentCostM.ReadWattage;
  CurrentCostP.CurrentCostControl -> CurrentCostM.CurrentCostControl;
  CurrentCostP.SensingTimer ->SensingTimer;
  
}

