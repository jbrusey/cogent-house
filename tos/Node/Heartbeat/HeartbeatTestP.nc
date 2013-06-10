// -*- c -*-
#include "printf.h"
#include "math.h"

module HeartbeatTestP @safe()
{
  uses {
    interface Boot;
    interface Heartbeat as HB;
    interface Timer<TMilli> as CheckTimer;
    interface Random;
    interface Leds;
  }
}

implementation
{
  int tests_run=0;
  char *result;
  
  static char* testUninitalised(void){
    mu_assert("Uninit Heartbeat is false",  !call HB.triggered());
    return 0;
  }

  static char* testInitalise(void){
    call HB.init();
  }


 static char* testTriggered(void){
    mu_assert("Init Heartbeat is false",  !call HB.triggered());
    call CheckTimer.startOneShot(16384);
    printf("17 seconds until result\n");
    printfflush();
    mu_assert(" Reset Heartbeat is false", ! call HB.triggered());
    return 0;
  }  
  
  static char* testReset(void){
    call HB.reset();
    mu_assert(" Reset Heartbeat is false", ! call HB.triggered());
    return 0;
  }   
   
  static char* all_tests(void) { 
    call Leds.led2On();
    mu_run_test(testUninitalised);
    mu_run_test(testInitalise);
    mu_run_test(testReset);
    mu_run_test(testTriggered);
    call Leds.led1Toggle(); 
    return 0;
  }

  event void CheckTimer.fired(){
     mu_assert("Heartbeat is True", call HB.triggered());

     if (!call HB.triggered())
     {
       printf("Tiggered Heartbeat is not True\n");
     }
     call Leds.led2Off();
     call Leds.led1Off();
     if (result != 0) {
       printf("%s\n", result);
       call Leds.led0On();
     }
     else {
       printf("ALL TESTS PASSED\n");
       call Leds.led1On();
     }
     printf("Tests run: %d\n", tests_run);
     printfflush();
  }

  event void Boot.booted()
  {
    all_tests(); 
  }
}
