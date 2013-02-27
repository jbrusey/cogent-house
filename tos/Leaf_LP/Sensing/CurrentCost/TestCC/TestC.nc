// -*- c -*-
#include "msp430usart.h"
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#include <stdint.h>
configuration TestC { }

implementation
{
  components MainC, CurrentCostM, TestP;
  components new TimerMilliC() as SensingTimer;
  components new TimerMilliC() as TimeoutTimer;
  components new TimerMilliC() as ResumeTimer;
  components new TimerMilliC() as FirstByteTimer;
  components new TimerMilliC() as ByteTimer;
  components HilTimerMilliC;
  components PrintfC, SerialStartC;

  TestP.Boot -> MainC.Boot;
  
  CurrentCostM.CurrentCostUartStream -> TestP;
  CurrentCostM.UartControl -> TestP;
  CurrentCostM.TimeoutTimer -> TimeoutTimer;
  CurrentCostM.ResumeTimer -> ResumeTimer;
  CurrentCostM.FirstByteTimer -> FirstByteTimer;
  CurrentCostM.LocalTime -> HilTimerMilliC;

  TestP.ReadWattage->CurrentCostM.ReadWattage;
  TestP.CurrentCostControl -> CurrentCostM.CurrentCostControl;
  TestP.SensingTimer ->SensingTimer;
  TestP.ByteTimer -> ByteTimer;
  
}

