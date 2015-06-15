// -*- c -*-
#include "printf.h"
#include "printfloat.h"
#define HIGH_COVARIANCE 1e20
#include "math.h"

module PassTestP @safe()
{
  uses {
    interface Boot;
    interface Filter as Pass;
    interface Random;
    interface Leds;
  }
}

implementation
{
  int tests_run=0; 
  
  static char* testPassFilter(void){
    float z;
    FilterState xnew;
    float i;

    call Pass.init(0., 0.);

    for (i = 1.; i < 2001.; i++) { 
      z = i;
      call Pass.filter(z, i * 1024, &xnew);
      /* printf("x="); printfloat(xnew.x); */
      /* printf(" dx="); printfloat(xnew.dx); */
      /* printf("\n"); */
      if (i < 2.f) 
	mu_assert("first dx should be zero", xnew.x == z && xnew.dx == 0.f);
      else
	mu_assert("Filtered wrong", xnew.x == z && xnew.dx == 1.f);
    }


    return 0;
  }
   
   
   
  static char* all_tests(void) { 
    /* call Leds.led2On(); */
    mu_run_test(testPassFilter);  
    /* call Leds.led1Toggle();  */
    return 0;
  }


  event void Boot.booted()
  {
    char *result = all_tests();
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
  

}
