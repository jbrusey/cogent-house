// -*- c -*-
/*************************************************************
 * SwitchedAnalogTestC - configuration
 * 
 * Test SwitchedAnalogC by printing out voltage level every second
 *
 * J. Brusey, 16/5/2015
 *************************************************************/
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#include "printfloat.h"
#include <Msp430Adc12.h>

configuration SwitchedAnalogTestC {}

implementation {

  components MainC;

  //define components that will be used
  components LedsC;
  components new SwitchedAnalog3C(INPUT_CHANNEL_A1, 10*1024) as MySwitchedAnalog;
  components SwitchedAnalogTestP;
  components PrintfC;
  components SerialStartC;

  //Wire componants to app
  SwitchedAnalogTestP.Boot -> MainC;
  SwitchedAnalogTestP.Leds -> LedsC;

  SwitchedAnalogTestP.ReadFloat -> MySwitchedAnalog;
  
}
