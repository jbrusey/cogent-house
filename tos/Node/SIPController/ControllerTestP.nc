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
    interface TransmissionControl;
  }
}

implementation
{

  event void Boot.booted(){
    call TEMPSIPRead.init(0.25, 1, 0.1, 0.1);
    call HUMSIPRead.init(0.25, 1, 0.1, 0.1);
    call SenseTimer.startPeriodic(DEF_SENSE_PERIOD);
  }

  event void SenseTimer.fired(){
    call TEMPSIPRead.read();
    call HUMSIPRead.read();
  }

  event void TEMPSIPRead.readDone(error_t result, FilterState* data){
    printf("Temp: ");
    printfloat2(data->x);
    printf(", ");
    printfloat2(data->dx);
    printf(", ");
    printfloat2(data->z);
    printf("\n");
  }

  event void HUMSIPRead.readDone(error_t result, FilterState* data){
    printf("Hum: ");
    printfloat2(data->x);
    printf(", ");
    printfloat2(data->dx);
    printf(", ");
    printfloat2(data->z);
    printf("\n");
    printf("To Send: %u\n", call TransmissionControl.hasEvent());
    printfflush();
    call TransmissionControl.transmissionDone();
  }


}
