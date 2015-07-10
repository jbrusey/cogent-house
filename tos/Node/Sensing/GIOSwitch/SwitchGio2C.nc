// -*- c -*-
configuration SwitchGio2C { 
    provides interface StdControl as SwitchControl;
}

implementation
{
#ifdef DEBUG
  components LedsC;
#endif
  components new GIOSwitchM() as SwitchM;
  components HplMsp430GeneralIOC as GIO;

  SwitchM.SwitchControl = SwitchControl;
  SwitchM.Switch -> GIO.Port23;
#ifdef DEBUG
  SwitchM.Leds -> LedsC;
#endif
}

