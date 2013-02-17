// -*- c -*-
#include "minunit.h"
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

  event void EventRead.readDone(error_t result, float* data) {
    //read in value from data
    float* currentPct;
    currentPct = data;
    var = currentPct[2];
    test=result;
  }
  
  
  static char* testEventDetector(void){
    while (test != SUCCESS)
      {
	call EventRead.read();
      }
    printf("Reading is : "); printfloat2(var);
    mu_assert("Reading: var != 10", var == 10.);
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
    }
    printf("Tests run: %d\n", tests_run);
    printfflush();
    
  }
  

}
