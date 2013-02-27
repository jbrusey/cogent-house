// -*- c -*-
#include "msp430usart.h"
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
configuration HeatMeterC { }

implementation
{
  components MainC, HeatMeterP, HeatMeterM, LedsC;
  components new TimerMilliC() as SensingTimer;
  components HilTimerMilliC;
  components PrintfC, SerialStartC;
  components HplMsp430InterruptP as GIOInterrupt;
  components HplMsp430GeneralIOC as GIO;
	
  
  HeatMeterP.Boot -> MainC.Boot;
  HeatMeterM.Leds -> LedsC;
  HeatMeterM.EnergyInput -> GIO.Port26;
  HeatMeterM.EnergyInterrupt -> GIOInterrupt.Port26; //set to read from gio3
  HeatMeterM.VolumeInput -> GIO.Port23;
  HeatMeterM.VolumeInterrupt -> GIOInterrupt.Port23; //set to read from gio2
  
  HeatMeterP.LocalTime -> HilTimerMilliC;
  HeatMeterP.ReadHeatMeter->HeatMeterM.ReadHeatMeter;
  HeatMeterP.HeatMeterControl -> HeatMeterM.HeatMeterControl;
  HeatMeterP.SensingTimer ->SensingTimer; 
}

