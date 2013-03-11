#include <Timer.h>

#define TIMER_PERIOD_MILLI 200

module DigitalP {
	uses interface Boot;
	uses interface Leds;
	uses interface HplMsp430GeneralIO as GIO;
	uses interface Timer<TMilli> as PulseTimer;
	uses interface Timer<TMilli> as PulseEnd;
}
implementation {
   
	event void Boot.booted() {
		call GIO.makeOutput(); //make it input
		call GIO.set();
		call PulseTimer.startPeriodic(307200);	
	}

	event void PulseTimer.fired() {
        call Leds.led2On();
    	call GIO.clr();	
    	call PulseEnd.startOneShot(410);
	}

	event void PulseEnd.fired() {
		call Leds.led2Off();
		call GIO.set();
	}


}
