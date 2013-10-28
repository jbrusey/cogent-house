// -*- c -*-
#include "msp430usart.h"
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
configuration ACReaderC { }

implementation
{
  components MainC, ACReaderP, LedsC;
  components new ACStatusM() as ACStatusM;
  components new TimerMilliC() as SensingTimer;
  components HilTimerMilliC;
  components PrintfC, SerialStartC;
  components HplMsp430GeneralIOC as GIO;
	
  
  ACReaderP.Boot -> MainC.Boot;
  ACReaderP.Leds -> LedsC;
  ACStatusM.ACInput -> GIO.Port26;
  
  
  ACReaderP.LocalTime -> HilTimerMilliC;
  ACReaderP.ReadAC->ACStatusM.ReadAC;
  ACReaderP.ACControl -> ACStatusM.ACControl;
  ACReaderP.SensingTimer ->SensingTimer; 
}

