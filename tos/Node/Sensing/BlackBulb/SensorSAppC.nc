#define NEW_PRINTF_SEMANTICS
#include "printf.h"

configuration SensorSAppC {}

implementation {

  components MainC;

  //define components that will be used
  components SensorSC as App, LedsC;
  components new SensirionSht11C(); 
  components new TimerMilliC();
  components PrintfC;
  components SerialStartC;

  components new BlackBulbC() as BB;
  components BlackBulbM;


  //Wire componants to app
	
  App.Boot -> MainC;
  App.Leds ->  LedsC;
  App.MilliTimer -> TimerMilliC;
  BlackBulbM.GetBB -> BB;
  App.ReadBB->BlackBulbM.ReadBB;

}
