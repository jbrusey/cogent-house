// -*- c -*-
#include "printf.h"
#define HIGH_COVARIANCE 1e20
#include "math.h"

module KalmanTestP @safe()
{
  uses {
    interface Boot;
    interface Filter as KalmanDeltaSine;
    interface Filter as KalmanDelta;
    interface Filter as KalmanDeltaSineDiscretised;
    interface Filter as KalmanDeltaSineDiscretisedRandom;
    interface Filter as KalmanTimeOverflow;
    interface Random;
    interface Leds;
  }
}

implementation
{
  int tests_run=0;

  static char* test_mat22_add_v(void) {
    
    vec2 v1 = {10.02, 0.02}, v2 = {0., 0}, v3, v4 = {10.02, 0.02};
    
    mat22_add_v( v1, v2, v3);
    
    mu_assert("add_v failed", v3[0] == v4[0] &&
	      v3[1] == v4[1]);
  
  
    return 0;
  }

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

  static char* testKalmanDeltaSine(void){
    float sse;
    float z;
    float v[2];
    float err;
    float i;

    sse = 0.;
    for (i = 1; i < 2002; i++) { 
      z = sin(i / 2000. * M_PI);
      call KalmanDeltaSine.filter(z, i * 1024, v);
      err = v[0] - (z);
      sse += err * err;
    }
    mu_assert("Sine: sse < 0.03", sse < 0.03);
    return 0;
  }
   
  static char* testKalmanDelta(void) {
    float sse;
    float z;
    float v[2];
    float err;
    float i;

    sse = 0.;
    for (i = 1; i < 2001; i++) { 
      z = ((i / 64.) + 10.);
      call KalmanDelta.filter(z, i * 1024, v);
      
      err = v[0] - z;
      sse += err * err;
    }

    mu_assert("Delta: v[1] not 1/64", v[1] == 1./64.); //1/64
    mu_assert("Delta: v[0] not 10 +2000/64.", v[0] == 10. + 2000. /64.); // (added 0.1 because of rounding of floats
    mu_assert("Delta: sse == 0", sse <= 0.);
    return 0;
  }

  static char* testKalmanDeltaSineDiscretised(void){
    float sse;
    float z;
    float z2;
    float v[2];
    float err;
    float i;
    
    sse = 0.;
    for (i = 1; i < 2002; i++) { 
      z = sin(i / 2000. * M_PI);
      z2 = floor(z * 10. + 0.5) /10.;
      
      call KalmanDeltaSineDiscretised.filter(z2, i * 1024, v);

      err = v[0] - z;
      sse += err * err;
    }

    /* printf("\n"); */
    /* mse = sse/2001.; */
    /* printf("DD: mse is "); printfloat2(mse); */
    /* printf("\n"); */
    mu_assert("DeltaDiscretised: mse is too large", (sse / 2001.) < 6);
    return 0;
  }
  
  static char* testKalmanDeltaSineDiscretisedRandom(void){
    float sse;
    float z;
    float z2;
    float v[2];
    float err;
    float i;
    
    sse = 0.;
    for (i = 1; i < 2002; i++) { 
      z = sin(i / 2000. * M_PI);
      z2 = floor(z * 10. + 0.5) /10.;
      
      // add in a random in the range [-0.05, 0.05]
      z2 += (float) call Random.rand16() / 655360. - 0.05;
      call KalmanDeltaSineDiscretisedRandom.filter(z2, i * 1024, v);

      err = v[0] - z;
      sse += err * err;
    }
    mu_assert("DeltaDiscretisedRandom: mse is too large", (sse / 2001.) < 0.01);
    return 0;
  }
  
  static char* testTimeOverflow(void){
    float sse;
    float z;
    float z2;
    float v[2];
    float err;
    float i;
    uint32_t t = 1;
    
    sse = 0.;
    for (i = 1; i < 2002; i++, t += (UINT32_MAX / 100)) { 
      z = sin(i / 2000. * M_PI);
      z2 = floor(z * 10. + 0.5) /10.;
      
      // add in a random in the range [-0.05, 0.05]
      z2 += (float) call Random.rand16() / 655360. - 0.05;
      call KalmanTimeOverflow.filter(z2, t, v);

      err = v[0] - z;
      sse += err * err;
    }

    mu_assert("TimeOverflow: mse is too large", (sse / 2001.) < 0.01);
    return 0;
  }

   
  static char* all_tests(void) { 
    mu_run_test(test_mat22_add_v); 
    call Leds.led2On();
    mu_run_test(testKalmanDeltaSine);  //Not working
    call Leds.led1Toggle(); 
    mu_run_test(testKalmanDelta); //Not Working
    call Leds.led1Toggle(); 
    mu_run_test(testKalmanDeltaSineDiscretised);
    call Leds.led1Toggle(); 
    mu_run_test(testKalmanDeltaSineDiscretisedRandom);
    call Leds.led1Toggle(); 
    mu_run_test(testTimeOverflow);
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
