// -*- c -*-
#include "printf.h"
#include "printfloat.h"
module PulseReaderP
{
  uses {
    interface Boot;
    interface Read<float> as ReadPulse;
    interface StdControl as PulseControl;
    interface Timer<TMilli> as SensingTimer;
    interface LocalTime<TMilli>;
#ifdef DEBUG
    interface Leds;
#endif
  }
}

implementation
{
  uint32_t sample = 0;

  enum {
    PERIOD = 10240
  };
  
  event void Boot.booted()
  {
    printf("Boot\n");
    call SensingTimer.startOneShot(PERIOD);
    call PulseControl.start();
  }  
  
  event void SensingTimer.fired() {
    if (sample != 10) {
      printf("start read %lu\n", ++sample);
      printfflush();
      call ReadPulse.read();
    }
    else {
      printf("testing shutting it down\n");
      printfflush();
      call PulseControl.stop();
      call PulseControl.start();
      call SensingTimer.startOneShot(PERIOD);
      sample++;
    }

  }
  
  
  event void ReadPulse.readDone(error_t result, float data) {
    if (result == SUCCESS) {
      printf("interrupt count: ");
      printfloat(data);
      printf("\n");
    }
    else
      printf("readDone no data\n");
    
    printfflush();
    call SensingTimer.startOneShot(PERIOD);
  }
}
