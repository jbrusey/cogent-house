#include "Timer.h"
#include "../PolyClass/horner.c"
module SensorSC
{
	//setup and define the interfaces that will be used
	uses
	{
		interface Timer<TMilli> as MilliTimer;
		interface Boot;
		interface Leds;
		interface Read<float> as ReadBB;
	}
}
implementation
{
	float bb;
	
	//Start the node
	event void Boot.booted()
	{
		call MilliTimer.startPeriodic(1024);
	}

	//When timer is fired get sensor readings, calc comfort and send result if there is a change
	event void MilliTimer.fired() {
		call ReadBB.read();
	}

	void printfFloat(float toBePrinted) {
		uint32_t fi, f0, f1, f2;
		char c;
		float f = toBePrinted;

		if (f<0){
			c = '-'; f = -f;
		} else {
			c = ' ';
		}

		// integer portion.
		fi = (uint32_t) f;

		// decimal portion...get index for up to 3 decimal places.
		f = f - ((float) fi);
		f0 = f*10;   f0 %= 10;
		f1 = f*100;  f1 %= 10;
		f2 = f*1000; f2 %= 10;
		printf("%c%ld.%d%d%d\n", c, fi, (uint8_t) f0, (uint8_t) f1, (uint8_t) f2);
	}



	event void ReadBB.readDone(error_t result, float data) {
		bb=data;
	        printf("BB value: ");
		printfFloat(bb);
        	printf("\n");
  	        printfflush();
	}

}

