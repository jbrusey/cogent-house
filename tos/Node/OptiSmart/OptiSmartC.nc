// -*- c -*-
#include "msp430usart.h"
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
configuration OptiSmartC { }

implementation
{
  components MainC, OptiSmartP, OptiSmartM, LedsC;
  components new TimerMilliC() as SensingTimer;
  components HilTimerMilliC;
  components PrintfC, SerialStartC;
  components HplMsp430InterruptP as GIOInterrupt;
  components HplMsp430GeneralIOC as GIO;
	
  
  OptiSmartP.Boot -> MainC.Boot;
  OptiSmartM.Leds -> LedsC;
  OptiSmartM.EnergyInput -> GIO.Port26;
  OptiSmartM.EnergyInterrupt -> GIOInterrupt.Port26; //set to read from gio3
  
  OptiSmartP.LocalTime -> HilTimerMilliC;
  OptiSmartP.ReadOpti->OptiSmartM.ReadOpti;
  OptiSmartP.OptiControl -> OptiSmartM.OptiControl;
  OptiSmartP.SensingTimer ->SensingTimer; 
}

