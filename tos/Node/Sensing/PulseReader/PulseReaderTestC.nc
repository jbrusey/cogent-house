// -*- c -*-
#include "msp430usart.h"
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
configuration PulseReaderTestC { }

implementation
{
  components MainC, PulseReaderP;
#ifdef DEBUG
  components LedsC;
#endif
  components new TimerMilliC() as SensingTimer;
  components HilTimerMilliC;
  components PrintfC, SerialStartC;
  components HplMsp430InterruptP as GIOInterrupt;
  components HplMsp430GeneralIOC as GIO;
  components new AlarmMilli32C() as MilliAlarm;

  components PulseGio2C;
  
  PulseReaderP.Boot -> MainC.Boot;
  
  PulseReaderP.LocalTime -> HilTimerMilliC;
  PulseReaderP.ReadPulse->PulseGio2C.ReadPulse;
  PulseReaderP.PulseControl -> PulseGio2C.PulseControl;
  PulseReaderP.SensingTimer ->SensingTimer; 
}

