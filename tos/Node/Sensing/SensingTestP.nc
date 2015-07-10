// -*- c -*-


#include "printf.h"
#include "printfloat.h"
#include "minunit.h"

#include "Packets.h"

module SensingTestP
{
  uses {
    interface Boot;
    interface Read<bool> as Sensing;
    interface AccessibleBitVector as Configured;
    interface PackState;
    
    interface Leds;
  }
}

implementation
{
  int tests_run=0;

  static char* all_tests(void);

  event void Boot.booted()
  {
    char * result;
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

  /** 
   * @return 'char * NTS' error 
   */ 
  static char* test_sense1(void) { 
    call Configured.clearAll();
    call Configured.set(RS_TEMPERATURE);
    call Configured.set(RS_HUMIDITY);
    call Configured.set(RS_VOLTAGE);
    call Configured.set(RS_ADC_0);
    call Configured.set(RS_ADC_1);
    call Configured.set(RS_ADC_2);
    call Sensing.read();
    return 0;
  }

  static char* all_tests(void) { 
    mu_run_test(test_sense1); 
    return 0;

  }

  event void Sensing.readDone(error_t result, bool val) { 
    packed_state_t ps;
    uint16_t pslen;
    int i;
    printf("read done : %d %d\n", result, (int) val);
    printfflush();

    if (result == SUCCESS) { 
      pslen = call PackState.pack(&ps);
      /* printf("mask = "); */
      /* for (i = 0; i < sizeof (ps.mask); i++) {  */
      /* 	printf("%02x ", ps.mask[i]); */
      /* } */
      /* printf("\n"); */

      for (i = 0; i < pslen; i++) { 
	printf("value %d = ", i);
	printfloat(ps.p[i]);
	printf("\n");
	printfflush();
      }
    }

  }

}
