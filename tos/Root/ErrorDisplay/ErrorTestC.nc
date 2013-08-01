// -*- c -*-
#include "../../Packets.h"
configuration ErrorTestC {
}
implementation
{
  components ErrorTestP, MainC, LedsC;

  ErrorTestP.Boot -> MainC;
  ErrorTestP.Leds -> LedsC;

	
  components new TimerMilliC() as ErrorDisplayTimer;
  components ErrorDisplayM;
  ErrorDisplayM.ErrorDisplayTimer -> ErrorDisplayTimer;
  ErrorDisplayM.Leds -> LedsC;
  ErrorTestP.ErrorDisplayControl -> ErrorDisplayM.ErrorDisplayControl;
  ErrorTestP.ErrorDisplay -> ErrorDisplayM.ErrorDisplay;
}
