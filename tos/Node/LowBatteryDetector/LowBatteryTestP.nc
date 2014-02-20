// -*- c -*-
#include "minunit.h"
#include "printfloat.h"
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




  event void LowBatt.readDone(error_t result, float data) {
    //read in value from data
    var = data;
  }
  
 
  static char* testLowBattery(void){
    int i;
    for (i = 0; i < 7; i++) { 
      call LowBatt.read();
      printf("\nReading is : "); printfloat(var);
    }
    printf("\nReading is : "); printfloat(var);
    mu_assert("\nReading: var < 2.31", var < 2.31);
    mu_assert("\nLow batt detected", call LowBatt.hasEvent());
    return 0;
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
