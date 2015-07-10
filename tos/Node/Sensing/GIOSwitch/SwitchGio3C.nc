// -*- c -*-
configuration SwitchGio3C { 
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
  SwitchM.Switch -> GIO.Port26;
#ifdef DEBUG
  SwitchM.Leds -> LedsC;
#endif
}

