// -*- c -*-
#include "msp430usart.h"
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
configuration PulseReaderC { }

implementation
{
  components MainC, PulseReaderP, PulseReaderM, LedsC;
  components new TimerMilliC() as SensingTimer;
  components HilTimerMilliC;
  components PrintfC, SerialStartC;
  components HplMsp430InterruptP as GIOInterrupt;
  components HplMsp430GeneralIOC as GIO;
	
  
  PulseReaderP.Boot -> MainC.Boot;
  PulseReaderM.Leds -> LedsC;
  PulseReaderM.EnergyInput -> GIO.Port26;
  PulseReaderM.EnergyInterrupt -> GIOInterrupt.Port26; //set to read from gio3
  
  PulseReaderP.LocalTime -> HilTimerMilliC;
  PulseReaderP.ReadPulse->PulseReaderM.ReadPulse;
  PulseReaderP.PulseControl -> PulseReaderM.PulseControl;
  PulseReaderP.SensingTimer ->SensingTimer; 
}

