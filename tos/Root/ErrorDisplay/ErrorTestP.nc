// -*- c -*-
#include "AM.h"
#include "Serial.h"


module ErrorTestP @safe() {
  uses {
      interface Boot;

      //errors
      interface StdControl as ErrorDisplayControl;
      interface ErrorDisplay;
      interface Leds;
    }
    
  provides interface Intercept as RadioIntercept[am_id_t amid];
}

implementation
{
  event void Boot.booted()
  {
    call ErrorDisplayControl.start();
    call ErrorDisplay.add(1);
    call ErrorDisplay.add(5);
    call ErrorDisplay.add(7);
  }

}
