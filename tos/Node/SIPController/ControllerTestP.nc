// -*- c -*-

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

  void printfloat2( float v) {
    int i = (int) v;
    int j;

    if (isnan(v)) {
      printf("nan");
      return;
    }
    if (isinf(v)) {
      printf("inf");
      return;
    }

    if (v < 0) {
      printf("-");
      printfloat2(-v);
      return;
    }
    if (v > 1e9) {
      printf("big");
      return;
    }

    printf("%d.", i);

    v -= i;

    j = 0;
    while (j < 20 && v > 0.) {
      v *= 10.;
      i = (int) v;
      v -= i;
      printf("%d", i);  
      j ++;
    }
  }


  event void Boot.booted(){
    call TEMPSIPRead.init(0.25, TRUE, 0., 0., FALSE, 0.1, 0.1);
    call HUMSIPRead.init(0.25, TRUE, 0., 0., FALSE, 0.1, 0.1);
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
