// -*- c -*-
#define NEW_PRINTF_SEMANTICS
#include "printf.h"


configuration LowBatteryTestC {}

implementation
{
  //const float Thresh = 3.;
  components MainC,LowBatteryTestP;
  components LowBatteryC;
  components SerialStartC;
  components DemoBatteryM;
  components PrintfC;


  LowBatteryC.BatteryRead -> DemoBatteryM.Read;
  LowBatteryTestP.LowBatt -> LowBatteryC.BNController;
  LowBatteryTestP.Boot -> MainC.Boot; 
}

