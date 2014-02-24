// -*- c -*-
#include "printfloat.h"

module ControllerTestP @safe()
{
  uses {
    interface Boot;
    interface Random;
    interface Leds;
    interface Timer<TMilli> as SenseTimer;
    interface SIPController<FilterState *> as TEMPSIPRead;
    interface SIPController<FilterState *> as HUMSIPRead;
    interface SIPController<FilterState *> as ReadHMEnergy;
    interface SIPController<FilterState *> as ReadOpti;
    interface StdControl as HMEnergyControl;
    interface StdControl as OptiControl;
    interface TransmissionControl;
    interface BitVector as ExpectReadDone;
  }
}

implementation
{
  const char *sensor_names[] = {"temperature",
				"humidity",
				"hm-energy",
				"opti"
  };


  event void Boot.booted(){
    int i;
    call TEMPSIPRead.init(0.25, 1, 0.1, 0.1);
    call HUMSIPRead.init(0.25, 1, 0.1, 0.1);
    call ReadHMEnergy.init(10, 1, 0, 0);
    call ReadOpti.init(1, 1, 0, 0);
    call HMEnergyControl.start();
    call SenseTimer.startPeriodic(DEF_SENSE_PERIOD);

    for (i = 0; i < RS_SIZE; i++) 
      call ExpectReadDone.clear(i);
  }

  event void SenseTimer.fired(){
    int i;
    /* note: only first three sensors are included: the fourth would
       overlap and shouldn't trigger */
    for (i = 0; i < 3; i++) {
      call ExpectReadDone.set(i);
    }
    call TEMPSIPRead.read();
    call HUMSIPRead.read();
    call ReadHMEnergy.read();
  }

  task void check_complete() { 
    int i;
    bool eventful;
    bool expecting = FALSE;
    for (i = 0; i < RS_SIZE; i++) 
      expecting = expecting || call ExpectReadDone.get(i);

    if (! expecting) {
      eventful = call TransmissionControl.hasEvent();
      printf("Will send?: %u\n", eventful);
      printfflush();
      if (eventful) 
	call TransmissionControl.transmissionDone();
      for (i = 0; i < RS_SIZE; i++) 
	call ExpectReadDone.clear(i);
    }
  }

  void read_done(int i, error_t result, FilterState* data) { 
    call ExpectReadDone.clear(i);
    printf("%s: ", sensor_names[i]);
    printfloat(data->x);
    printf(", ");
    printfloat(data->dx);
    printf(", ");
    printfloat(data->z);
    printf("\n");
    printfflush();
    post check_complete();
  }

  event void TEMPSIPRead.readDone(error_t result, FilterState* data){
    read_done(0, result, data);
  }

  event void HUMSIPRead.readDone(error_t result, FilterState* data){
    read_done(1, result, data);
  }
  
  event void ReadHMEnergy.readDone(error_t result, FilterState* data){
    read_done(2, result, data);
  }

  event void ReadOpti.readDone(error_t result, FilterState* data){
    read_done(3, result, data);
  }

}
