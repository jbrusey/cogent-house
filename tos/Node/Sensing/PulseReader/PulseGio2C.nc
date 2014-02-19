// -*- c -*-
configuration PulseGio2C { 
    provides interface Read<float> as ReadPulse;
    provides interface StdControl as PulseControl;
}

implementation
{
#ifdef DEBUG
  components LedsC;
#endif
  components new PulseReaderM() as PulseReaderM;
  components HplMsp430InterruptP as GIOInterrupt;
  components HplMsp430GeneralIOC as GIO;
  components new AlarmMilli32C() as MilliAlarm;

  PulseReaderM.ReadPulse = ReadPulse;
  PulseReaderM.PulseControl = PulseControl;
	
#ifdef DEBUG
  PulseReaderM.Leds -> LedsC;
#endif
  PulseReaderM.Input -> GIO.Port23;
  PulseReaderM.Interrupt -> GIOInterrupt.Port23; //set to read from gio2
  PulseReaderM.Alarm -> MilliAlarm;
}

