// -*- c -*-
#include "printf.h"
#define HIGH_COVARIANCE 1e20
#include "math.h"

module DEWMATestP @safe()
{
  uses {
    interface Boot;
    interface Filter as DEWMASine;
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
    for (i = 1.; i < 2001.; i++) { 
      z = ((i / 64.) + 10.);
      call DEWMASine.filter(z, i * 1024, v);
      err = v[0] - (z);
      sse += err * err;
    }
    printf("V[0] ");
    printfloat2(v[0]);
    printf("\n");
    
    printf("V[1] ");
    printfloat2(v[1]);
    printf("\n");
    
    printf("sse ");
    printfloat2(sse);
    printf("\n");

    mu_assert("Sine: v[0] error", v[0] == 10.+2000./64.);
    mu_assert("Sine: v[1] error", v[1] == 1./64.); 
    mu_assert("Sine: sse < 0.03", sse < 0.03);

    return 0;
  }
   


   
  static char* all_tests(void) { 
    mu_run_test(test_mat22_add_v); 
    call Leds.led2On();
    mu_run_test(testKalmanDeltaSine);  //Not working
    call Leds.led1Toggle(); 
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
