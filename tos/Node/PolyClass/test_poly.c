#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "minunit.h"
#include "horner.h"


//float horner( int degree, float * coefs, float abscissa )

int tests_run = 0;
static char *
test_poly1(void) { 

	float value = 6748.0;

	float coeffs[] = {-39.60, 0.01};

	float result; 
	result=horner(sizeof(coeffs)/sizeof(float) - 1,coeffs,value);
//	printf("Temp: %f\n", result);
	mu_assert("test 1 wrong", result >= 27.879 && result <= 27.881);
	return 0;
}

static char *
test_poly2(void) {

	float value = 6748.0;

	float coeffs[] = {-39.60, 0.01, 999};

	float result; 
	// test incorrect degree specified
	result=horner(sizeof(coeffs)/sizeof(float),coeffs,value);
	//printf("Temp: %f\n", result);
	mu_assert("test 2 wrong", result < 27.879 || result > 27.881);
	return 0;
}
/*static char *
test_polymax(void) { 
  float result; 
  result=horner(sizeof(coeffs)/sizeof(float),coeffs,valuemax);
  mu_assert("ch1w not correct", result == 274726944766);
  return 0;
}


static char *
test_polymin(void) { 
  float result; 
  result=horner(sizeof(coeffs)/sizeof(float),coeffs,valuemin);
  mu_assert("ch1w not correct", result == 1);
  return 0;
}*/

//negative number check

static char *
all_tests(void) { 
  mu_run_test(test_poly1);
  mu_run_test(test_poly2);
  //mu_run_test(test_polymax);
  //mu_run_test(test_polymin);
  return 0;
}

int
main(void) {
  char *result = all_tests();
  if (result != 0) {
    printf("%s\n", result);
  }
  else {
    printf("ALL TESTS PASSED\n");
  }
  printf("Tests run: %d\n", tests_run);
  
  return result != 0;
 }


