// -*- c -*-
#include "minunit.h"
#include "printfloat.h"
module ExposureEventDetectorTestP @safe()
{
  uses {
    interface Boot;
    interface BNController<float*> as EventRead;
  }
}

implementation
{
  int tests_run=0;
  error_t test=FAIL;
  float var;

  event void EventRead.readDone(error_t result, float* data) {
    //read in value from data
    float* currentPct;
    currentPct = data;
    var = currentPct[2];
  }
  
 
  static char* testEventDetector(void){
    while (var < 10){
      call EventRead.read();
      printf("Reading is : "); printfloat(var);
      if (call EventRead.hasEvent()){
	printf("\nEvent!!!\n");
	mu_assert("Reading: var != 10", var == 1. || var ==10.);
	call EventRead.transmissionDone();
      }
      printf("\n\n");
    }
    return 0;
  }
     
  static char* all_tests(void) { 
    mu_run_test(testEventDetector);
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
      //TODO: turn on green led
    }
    printf("Tests run: %d\n", tests_run);
    printfflush();
    
  }
  

}
