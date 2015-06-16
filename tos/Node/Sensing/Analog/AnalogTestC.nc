// -*- c -*-
/*************************************************************
 * AnalogTestC - configuration
 * 
 * Test AnalogC by printing out voltage level every second
 *
 * J. Brusey, 16/5/2015
 *************************************************************/
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#include "printfloat.h"
#include <Msp430Adc12.h>

configuration AnalogTestC {}

implementation {

  components MainC;

  //define components that will be used
  components LedsC;
  components new AnalogC(INPUT_CHANNEL_A0) as MyAnalog;
  components AnalogTestP;
  components new TimerMilliC();
  components PrintfC;
  components SerialStartC;

  //Wire componants to app
  AnalogTestP.Boot -> MainC;
  AnalogTestP.Leds -> LedsC;
  AnalogTestP.MilliTimer -> TimerMilliC;

  AnalogTestP.ReadFloat -> MyAnalog;
  
}
