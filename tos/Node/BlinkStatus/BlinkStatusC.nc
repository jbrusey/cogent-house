// -*- c -*-
configuration BlinkStatusC { 
  provides interface BlinkStatus;
}

implementation
{
  components new TimerMilliC() as BlinkTimer;
  components LedsC;

  components BlinkStatusP;

  BlinkStatusP.Leds -> LedsC;
  BlinkStatusP.BlinkTimer -> BlinkTimer;
  BlinkStatusP.BlinkStatus = BlinkStatus;
}

