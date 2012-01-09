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
    int count=0;
    
	event void Boot.booted() {
		call GIO.makeOutput(); //make it input
		call GIO.set();
		call PulseTimer.startPeriodic(1024);	

	}

	event void PulseTimer.fired() {
	    count+=1;
	    if (count < 100){
    		call Leds.led2On();
	    	call GIO.clr();	
	    	call PulseEnd.startOneShot(410);
	    }
	    else
	    {
	        call PulseTimer.stop();
	    }
	}

	event void PulseEnd.fired() {
		call Leds.led2Off();
		call GIO.set();
	}


}
