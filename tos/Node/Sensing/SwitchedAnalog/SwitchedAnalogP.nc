// -*- c -*-
/*************************************************************
 * SwitchedAnalogP - module
 * 
 * Turn on GIO output and wait a defined time before reading
 * from ADC. 
 *
 * J. Brusey, 27/7/2015
 *************************************************************/

#include <Msp430Adc12.h>
generic module SwitchedAnalogP(uint16_t warm_up_millis) {
  provides {
    interface Read<float> as ReadFloat;
  }

  uses { 
    interface Read<float> as ReadDeviceFloat;
    interface StdControl as SwitchControl;
    interface Timer<TMilli> as WarmUpTimer;
  }

}
implementation {

  /** ReadFloat.read() starts the read cycle by passing the request to the low-level driver
   */
  command error_t ReadFloat.read() {
    call SwitchControl.start();
    call WarmUpTimer.startOneShot(warm_up_millis);
    
    return SUCCESS;
  }

  /** WarmUpTimer.fired is called when the warm up timer has finished and we are ready to read the adc port */

  event void WarmUpTimer.fired() {
    error_t ok = call ReadDeviceFloat.read();
    if (ok != SUCCESS) {
      call SwitchControl.stop();
      signal ReadFloat.readDone(ok, 0.);
    }
  }


  /** ReadDeviceFloat.readDone is signalled from the low-level driver
      when a sample has been taken.
   */
  event void ReadDeviceFloat.readDone(error_t result, float val) {
    call SwitchControl.stop();
    signal ReadFloat.readDone(result, val);
  }
}
