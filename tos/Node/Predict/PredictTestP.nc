// -*- c -*-
#include "printf.h"
#include "math.h"

module PredictTestP @safe()
{
  uses {
    interface Boot;
    interface Random;
    interface Leds;
    interface Predict;
  }
}

implementation
{
  int tests_run=0;
  FilterState sink_state;

  static char* testPredict(void){
    float state_xs;

    //Create dummy sink state
    sink_state.x = 0;
    sink_state.dx = 1;
    sink_state.time = 0;


    //Create dummy sink state
    state_xs = call Predict.predictState(&sink_state, 100L*1024L);  //Predict state 100 readings in the future (should return 100)
    mu_assert("Prediction is not 100",  state_xs == 100);
    //Run predict
    return 0;
  }


  static char* testPredict2(void){
    float state_xs;

    //Create dummy sink state
    sink_state.x = 0;
    sink_state.dx = 1;
    sink_state.time = 0;


    //Create dummy sink state
    state_xs = call Predict.predictState(&sink_state, 200L*1024L); 
    mu_assert("Prediction is not 200",  state_xs == 200);
    //Run predict
    return 0;
  }
  
 
  static char* all_tests(void) { 
    call Leds.led2On();
    mu_run_test(testPredict);
    mu_run_test(testPredict2);
    call Leds.led1Toggle(); 
    return 0;
  }

  event void Boot.booted()
  {
    char *result;
    result = all_tests(); 

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
