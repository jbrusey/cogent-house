// -*- c -*-
#include "msp430usart.h"
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
configuration WindowReaderC { }

implementation
{
  components MainC, WindowReaderP, LedsC;
  components new WindowM() as WindowM;
  components new TimerMilliC() as SensingTimer;
  components HilTimerMilliC;
  components PrintfC, SerialStartC;
  components HplMsp430GeneralIOC as GIO;
	
  
  WindowReaderP.Boot -> MainC.Boot;
  WindowReaderP.Leds -> LedsC;
  WindowM.WindowInput -> GIO.Port23;
  
  
  WindowReaderP.LocalTime -> HilTimerMilliC;
  WindowReaderP.ReadWindow->WindowM.ReadWindow;
  WindowReaderP.WindowControl -> WindowM.WindowControl;
  WindowReaderP.SensingTimer ->SensingTimer; 
}

