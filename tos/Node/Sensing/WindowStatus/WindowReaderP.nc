// -*- c -*-
#include "printf.h"
#include "printfloat.h"
module WindowReaderP
{
  uses {
    interface Boot;
    interface Read<float> as ReadWindow;
    interface StdControl as WindowControl;
    interface Timer<TMilli> as SensingTimer;
    interface LocalTime<TMilli>;
    interface Leds;
  }
}

implementation
{
  bool started = FALSE;
  enum {
    PERIOD = 1024 * 10
  };
  
  event void Boot.booted()
  {
    printf("Boot\n");
    printfflush();
    call SensingTimer.startPeriodic(PERIOD);
  }
  
  event void SensingTimer.fired() {
    printf("start read\n");
    call ReadWindow.read();
  }
  
  
  event void ReadWindow.readDone(error_t result, float data) {
    error_t error;
    if (result == SUCCESS) {
      printf("State: ");
      printfloat(data);
      printf("\n");
    }
    else {
      printf("readDone no data\n");
      error = call WindowControl.start();
      printf("got start result %u\n", error);
      printfflush();
    }

    printfflush();      
  }
}
