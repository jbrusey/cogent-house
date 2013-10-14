#define NEW_PRINTF_SEMANTICS
#include "printf.h"

configuration SensorSAppC {}

implementation {

  components MainC;

  //define components that will be used
  components SensorSC as App, LedsC;
  components new TimerMilliC();
  components PrintfC;
  components SerialStartC;

  components new WindowC() as Window;
  components WindowM;

  //Wire componants to app
  App.Boot -> MainC;
  App.Leds ->  LedsC;
  App.MilliTimer -> TimerMilliC;
  WindowM.GetWindow -> Window;
  App.ReadWindow->WindowM.ReadWindow;
}
