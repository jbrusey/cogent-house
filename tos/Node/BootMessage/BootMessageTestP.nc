// -*- c -*-


#include "printf.h"
#include "minunit.h"

module BootMessageTestP
{
  uses {
    interface Boot;
    interface SplitControl as RadioControl;
    interface StdControl as CollectionControl;
    interface BootMessage;
    
    interface Leds;
  }
}

implementation
{
  int tests_run=0;

  event void Boot.booted()
  {
    call RadioControl.start();
  }

  /** 
   * @return 'char * NTS' error 
   */ 
  static char* test_bootmessage1(void) { 
    
    call BootMessage.send();
    return 0;
  }

  event void BootMessage.sendDone(error_t result) { 
    printf("sendDone returned %u\n", result);
    printfflush();
  }

  static char* all_tests(void) { 
    /* mu_run_test(test_bitset_iterator); */
    mu_run_test(test_bootmessage1); 
    return 0;

  }

  event void RadioControl.startDone(error_t err) {
    char *result;
    if (err == SUCCESS) {
      call CollectionControl.start();
      result = all_tests();
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
    else {
      printf("retrying radio start\n");
      printfflush();
      call RadioControl.start();
    }
  }

  event void RadioControl.stopDone(error_t err) { 
  }
}
