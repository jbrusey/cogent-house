// -*- c -*-
#include "printf.h"
#define HIGH_COVARIANCE 1e20
#include "math.h"

module DEWMATestP @safe()
{
  uses {
    interface Boot;
    interface Filter as Dewma;
    interface Random;
    interface Leds;
    interface Predict;
  }
}

implementation
{
  int tests_run=0;

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
  
char * test_dewma_not_using_rate_correctly(void)
{
    float z;
    FilterState x;
    uint32_t i;
    uint32_t t;
    call Dewma.init(0.2f,0.2f);
    for (i = 0; i < 129; i++) {
        t = i*10*8 ;
        z = t / 1024.0 * 12.1 + 4.5;
        call Dewma.filter(z, t, &x);
    }  

    printfloat2(x.x);
    printf("\n");
    printfloat2(x.dx);
    printf("\n");
    mu_assert("estimates after 100 iterations are wrong",
	      fabs(x.x - (121.f+4.5f) ) < 0.0001f);
    mu_assert("delta estimates after 100 iterations are wrong",
        fabs(x.dx - 12.1f) < 0.0001f);
    return 0;
    
    //16.4790019989013671875
    //0.12099983692169189453

}


  
  static char* test_dewma1(void){
    float z;
    FilterState x;
    uint32_t i;
    call Dewma.init(0.2f,0.2f);
    for (i = 0; i < 100; i++) {
      z = i * 12.1f + 4.5f;
      call Dewma.filter(z, i*1024, &x);
   }
   printfloat2(x.x);
   printf("\n");
   printfloat2(x.dx);
   printf("\n");
   mu_assert("estimates after 100 iterations are wrong",
	    fabs(x.x  - 1202.40083) < 0.0001);
   mu_assert("delta estimates after 100 iterations are wrong",
	    fabs(x.dx - 12.0999864) < 0.0001); 
  
    return 0;
  }

  
   
  static char * test_dewma2(void) 
  { 
    FilterState s1, s2;
    uint32_t c;
    float v;

    call Dewma.init(0.2f, 0.2f);


    c = 1024;
    call Dewma.filter(101.f, c, &s2);
    s1 = s2;
  
    c = 1024 + 512;
    v = call Predict.predictState(&s1, c);
  
    mu_assert("should stay flat",
	      v == 101.f);

    return 0;
  }

  static char * test_dewma3(void)
  {
    FilterState s2;
    uint32_t c;
    float v;

    call Dewma.init(0.99f, 0.99f);

    /* mu_assert("init not ok", */
    /* 	      d.count == 0 && */
    /* 	      d.alpha == 0.99f && */
    /* 	      d.beta == 0.99f); */

    c = 1024;
    call Dewma.filter(101.f, c, &s2);
    /*print_state(&s2);*/
  
    c = 1024 + 512;
    call Dewma.filter(103.f, c, &s2);
    /*print_state(&s2);*/
  
    c = 2048;

    call Dewma.filter(105.f, c, &s2);
    /*print_state(&s2);*/

    c = 3 * 1024;
    v = call Predict.predictState(&s2, c);
    /*print_state(&s2);*/
  
    /* printf("%f, %f\n", s2.x[0], s2.x[1]); */
    mu_assert("should roughly track trend",
	      fabs(v - 109.f) < 0.1 &&
	      fabs(s2.dx - 4.f) < 0.1);

    return 0;
  }


   
  static char* all_tests(void) { 
    mu_run_test(test_dewma2); 
    mu_run_test(test_dewma1);
    mu_run_test(test_dewma3);
    mu_run_test(test_dewma_not_using_rate_correctly);
    /* call Leds.led1Toggle();  */
    return 0;
  }


  event void Boot.booted()
  {

    char *result;
    printfflush();

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
