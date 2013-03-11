// -*- c -*-
#include "minunit.h"
module LowBatteryTestP @safe()
{
  uses {
    interface Boot;
    interface BNController<float> as LowBatt;
  }
}

implementation
{
  int tests_run=0;
  error_t test=FAIL;
  float var;



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

  event void LowBatt.readDone(error_t result, float data) {
    //read in value from data
    var = data;
  }
  
 
  static char* testLowBattery(void){
     call LowBatt.read();
     printf("\nReading is : "); printfloat2(var);
     call LowBatt.read();
     printf("\nReading is : "); printfloat2(var);
     call LowBatt.read();
     printf("\nReading is : "); printfloat2(var);
     call LowBatt.read();
     printf("\nReading is : "); printfloat2(var);
     call LowBatt.read();
     printf("\nReading is : "); printfloat2(var);
     call LowBatt.read();
     printf("\nReading is : "); printfloat2(var);
     call LowBatt.read();
     printf("\nReading is : "); printfloat2(var);
     mu_assert("\nReading: var != 10", var < 2.31);
     mu_assert("\nLow batt detected", call LowBatt.hasEvent());

  }
     
  static char* all_tests(void) { 
    mu_run_test(testLowBattery);
    return 0;
  }


  event void Boot.booted()
  {
    char *result = all_tests();
    if (result != 0) {
      printf("%s\n", result);
    }
    else {
      printf("ALL TESTS PASSED\n");
    }
    printf("Tests run: %d\n", tests_run);
    printfflush();
    
  }
  

}
