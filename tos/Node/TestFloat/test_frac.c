#include <stdio.h>
#include <assert.h>

typedef int int32_t ;
typedef unsigned int uint32_t;

enum {
  ITER = 4096 
};


  // see section 4.5 of Seminumerical Algorithms by D. Knuth
  typedef struct ratio { 
    int32_t quot;
    int32_t div;
  } ratio_t;

int bits(int32_t u) { 
  int i = 0;
  while (u != 0) {
    i++;
    u >>= 1;
  }
  return i;
}
      
  

  /** modern Euclid algorithm (section 4.5.2 DK-SNA) 
   */
   int32_t gcd(int32_t u, int32_t v) {
    int32_t r;
    if (u < 0) u = -u;
    if (v < 0) v = -v;
    for (;;) {
      assert(u > 0);
      if (v == 0)
	return u;
      r = u % v;
      u = v;
      v = r;
    }
  }
  
  /** see 4.5.1 of DK-SNA */
   void frac_add(ratio_t *w, ratio_t *u, ratio_t *v) { 
    int32_t d1, d2, t;
    assert(u->div > 0);
    assert(v->div > 0);
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
    assert(w->div > 0);
  }

   void frac_sub(ratio_t *result, ratio_t *first, ratio_t *second) {
    ratio_t tmp;
    tmp.quot = - second->quot;
    tmp.div = second->div;
    frac_add(result, first, &tmp);
  }

   void frac_times(ratio_t *w, ratio_t *u, ratio_t *v) {
    int32_t d1, d2;
    assert(u->div > 0);
    assert(v->div > 0);
    d1 = gcd(u->quot, v->div);
    d2 = gcd(u->div, v->quot);
    
    w->quot = (u->quot / d1) * (v->quot / d2);
    w->div = (u->div / d2) * (v->div / d1);
    assert(w->div > 0);
  }

  const int32_t BITTHRESHOLD = 1L << 16;
  const int32_t NEGTHRESHOLD = -1L << 16;
  void frac_slash(ratio_t *r) {
    // ensure that neither divisor nor quotient exceed 16 bits
    assert(r->div > 0);
    
    while (r->quot > BITTHRESHOLD || r->div > BITTHRESHOLD || r->quot < NEGTHRESHOLD) {
      r->quot /= 2;
      r->div /= 2;
    }
  }
      

void intTest(void) {
    int i;
    //uint32_t t;
    ratio_t z, x = {0,1}, alpha = {1,10}, tmp1, tmp2;

    //t = call LocalTime.get();
    
    for (i = 0; i < ITER; i++) { 
      z.quot = (i % 4096); // current reading
      z.div = 1;

      frac_sub(&tmp1, &z, &x);
      frac_slash(&tmp1);

      frac_times(&tmp2, &alpha, &tmp1);
      frac_slash(&tmp2);
      
      frac_add(&x, &tmp2, &x);
      // simple ewma
      //x += alpha * (z - x);
    }

    //printf("intTest time = %lu\n", call LocalTime.get() - t);

    printf("final value = %d / %d\n", x.quot, x.div);
  }    

int main(void) { 
  printf("starting\n");
  intTest();
  return 0;
}
