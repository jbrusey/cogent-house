// -*- c -*-
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#include "minunit.h"
#include <stdint.h>

configuration HeartbeatTestC {}

implementation
{
  components MainC, HeartbeatTestP;
  
  components PrintfC;
  components SerialStartC;
  components RandomC;
  components LedsC;
  components new HeartbeatC(15,1024) as HB;
  components new TimerMilliC() as CheckTimer;
  components new TimerMilliC() as HBTimer;

  HB.HeartbeatTimer -> HBTimer;
  HeartbeatTestP.CheckTimer -> CheckTimer;
  HeartbeatTestP.Boot -> MainC.Boot; 
  HeartbeatTestP.Random -> RandomC;
  HeartbeatTestP.Leds -> LedsC;
  HeartbeatTestP.HB -> HB;
}

