// -*- c -*-
#include "printf.h"
#include "minunit.h"

module TestFloatP
{
  uses {
    interface Boot;
    interface LocalTime<TMilli>;
  }
}

implementation
{

  int tests_run = 0;



  const int ITER = 4096 ;

  task void intTest();

  void printfFloat(float toBePrinted) {
    uint32_t fi, f0, f1, f2;
    char c;
    float f = toBePrinted;

    if (f<0){
      c = '-'; f = -f;
    } else {
      c = ' ';
    }

    // integer portion.
    fi = (uint32_t) f;

    // decimal portion...get index for up to 3 decimal places.
    f = f - ((float) fi);
    f0 = f*10;   f0 %= 10;
    f1 = f*100;  f1 %= 10;
    f2 = f*1000; f2 %= 10;
    printf("%c%ld.%d%d%d\n", c, fi, (uint8_t) f0, (uint8_t) f1, (uint8_t) f2);
  }

  task void floatTest() { 
    int i;
    uint32_t t;
    float alpha, z, x;
    


    t = call LocalTime.get();
    alpha = 0.1;
    
    x = 0.0;
    for (i = 0; i < ITER; i++) { 
      z = (float) (i % 4096); // current reading
      
      // simple ewma
      x += alpha * (z - x);
    }

    printf("floatTest time = %lu\n", call LocalTime.get() - t);

    printf("final value = ");
    printfFloat(x);
    printf("\n");
    printfflush();
    post intTest();
  }

  // see section 4.5 of Seminumerical Algorithms by D. Knuth
  typedef struct ratio { 
    int32_t quot, div;
  } ratio_t;

  /** modern Euclid algorithm (section 4.5.2 DK-SNA) 
   */
  inline int32_t gcd(int32_t u, int32_t v) {
    int32_t r;
    if (u < 0) u = -u;
    if (v < 0) v = -v;
    for (;;) {
      if (v == 0)
	return u;
      r = u % v;
      u = v;
      v = r;
    }
  }
  
  /** see 4.5.1 of DK-SNA */
  inline void frac_add(ratio_t *w, ratio_t *u, ratio_t *v) { 
    int32_t d1, d2, t;
    d1 = gcd(u->div, v->div); // d1 = gcd(u',v')
    if (d1 == 1) {
      w->quot = u->quot * v->div + u->div * v->quot;
      w->div = u->div * v->div;
    }
    else {
      t = u->quot * (v->div / d1) + v->quot * (u->div / d1);
      d2 = gcd(t, d1);
      w->quot = t / d2;
      w->div = (u->div / d1) * (v->div / d2);
    }
  }

  inline void frac_sub(ratio_t *result, ratio_t *first, ratio_t *second) {
    ratio_t tmp;
    tmp.quot = - second->quot;
    tmp.div = second->div;
    frac_add(result, first, &tmp);
  }

  inline void frac_times(ratio_t *w, ratio_t *u, ratio_t *v) {
    int32_t d1, d2;
    d1 = gcd(u->quot, v->div);
    d2 = gcd(u->div, v->quot);
    
    w->quot = (u->quot / d1) * (v->quot / d2);
    w->div = (u->div / d2) * (v->div / d1);
  }

  const int32_t BITTHRESHOLD = 1L << 16;
  const int32_t NEGTHRESHOLD = -1L << 16;
  void frac_slash(ratio_t *r) {
    // ensure that neither divisor nor quotient exceed 16 bits

    
    while (r->quot > BITTHRESHOLD || r->div > BITTHRESHOLD || r->quot < NEGTHRESHOLD) {
      r->quot >>= 1;
      r->div >>= 1;
    }
  }
      

  task void fixedPointTest(void);

  task void intTest(void) {
    int i;
    uint32_t t;
    ratio_t z, x = {0,1}, alpha = {1,10}, tmp1, tmp2;

    t = call LocalTime.get();
    
    for (i = 0; i < ITER; i++) { 
      z.quot = (i % 4096); // current reading
      z.div = 1;

      frac_sub(&tmp1, &z, &x);

      frac_times(&tmp2, &alpha, &tmp1);
      frac_slash(&tmp2);
      
      frac_add(&x, &tmp2, &x);
      // simple ewma
      //x += alpha * (z - x);
    }

    printf("intTest time = %lu\n", call LocalTime.get() - t);

    printf("final value = %lu / %lu\n", x.quot, x.div);
    printfflush();
    post fixedPointTest();
  }    

  enum { 
    BITSHIFT = 16
  };

  task void fixedPointTest(void) { 
    int i;
    uint32_t t;

    uint32_t x, z, dalpha;

    dalpha = 10;

    t = call LocalTime.get();
    x = 0;

    for (i = 0; i < ITER; i++) { 
      z = i % 4096;
      
      
      x += ((z << BITSHIFT) - x) / dalpha;
      
      // simple ewma
      //x += alpha * (z - x);
    }

    printf("fixedPointTest time = %lu\n", call LocalTime.get() - t);

    printf("final value = %ld\n", x);
    printfflush();
    post floatTest();
  }    

  ////////////////////////////////////////////////////////////
  // unit tests


  static char* test_frac(void) {

    ratio_t a = {7,66}, b = {17,12}, r1;//, c = {2,1}, r1, r2, r3;
    
    frac_add(&r1, &a, &b);
    frac_slash(&r1);

    mu_assert("7/66 + 17/12 != 67/44", r1.quot == 67 && r1.div == 44);
    
    frac_sub(&r1, &a, &b);
    
    mu_assert("7/66 - 17/12 != -173/132", r1.quot == -173 && r1.div == 132);

    frac_times(&r1, &a, &b);
    mu_assert("7/66 * 17/12 != 9/20", r1.quot == 7*17 && r1.div == 12*66);
 
  }

  static char* all_tests(void) { 
    mu_run_test(test_frac); 
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


    post floatTest();
  }

}
