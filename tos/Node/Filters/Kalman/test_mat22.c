#include "mat22.h"
#include <stdio.h>

#include "minunit.h"

char buf[1024];
int tests_run;

static char* test_mat22_mult(void) {

  mat22 m1, m2, m3;
  int i,j;

  m1[0][0] = 2.;
  m1[0][1] = 3.;
  m1[1][0] = 4.;
  m1[1][1] = 5.;

  m3[0][0] = 16.;
  m3[0][1] = 21.;
  m3[1][0] = 28.;
  m3[1][1] = 37.;

  mat22_mult(m1, m1, m2);

  for (i = 0; i < 2; i++) {
    for (j = 0; j < 2; j++) { 

      sprintf(buf, "mult m2 incorrect at %d, %d", i, j);
      mu_assert(buf, m2[i][j] == m3[i][j]);
    }
  }
  return 0;
}


static char* test_mat22_add(void) {

  mat22 m1, m2, m3;
  int i,j;

  m1[0][0] = 2.;
  m1[0][1] = 3.;
  m1[1][0] = 4.;
  m1[1][1] = 5.;

  m3[0][0] = 4.;
  m3[0][1] = 6.;
  m3[1][0] = 8.;
  m3[1][1] = 10.;

  mat22_add(m1, m1, m2);

  for (i = 0; i < 2; i++) {
    for (j = 0; j < 2; j++) { 

      sprintf(buf, "add m2 %f not %f off by %f at %d, %d", m2[i][j], m3[i][j], m2[i][j]- m3[i][j], i, j);
      mu_assert(buf, m2[i][j] == m3[i][j]);
    }
  }
  mu_assert("equals not ok", mat22_equals(m2, m3));
  return 0;
}


static char* test_mat22_dot_vs(void) {

  vec2 v1, v2;


  v1[0] = 3.;
  v1[1] = 4.;

  mat22_dot_vs(v1, 0.5, v2);

  mu_assert("dot_vs: v2[0] wrong", v2[0] == 1.5);
  mu_assert("dot_vs: v2[1] wrong", v2[1] == 2.);

  return 0;
}

static char* test_mat22_dot_vvt(void) {

  vec2 v1, v2;
  mat22 m;
  mat22 m1 = {{-3, 9}, {-4, 12}};

  v1[0] = 3.;
  v1[1] = 4.;

  v2[0] = -1.;
  v2[1] = 3.;

  mat22_dot_vvt(v1, v2, m);

  mu_assert("dot_vvt failed", mat22_equals(m, m1));

  return 0;
}

static char* test_mat22_dot_mv(void) {

  vec2 v1 = {5, 6}, v2, v3 = {17, -9};
  mat22 m = {{1, 2},{3, -4}};

  mat22_dot_mv( m, v1, v2);

  mu_assert("dot_vm failed", v2[0] == v3[0] &&
	    v2[1] == v3[1]);

  return 0;
}

static char* test_mat22_dot_vtv(void) {

  vec2 v1 = {1, 2}, v2 = {3, -4};
  float x;


  x = mat22_dot_vtv( v1, v2);

  mu_assert("dot_vtv failed", x == -5.);

  return 0;
}

static char* test_mat22_add_v(void) {

  vec2 v1 = {10.02, 0.02}, v2 = {0., 0}, v3, v4 = {10.02, 0.02};

  mat22_add_v( v1, v2, v3);
  
  mu_assert("add_v failed", v3[0] == v4[0] &&
	    v3[1] == v4[1]);
  
  
  return 0;
}

static char* test_mat22_sub(void) {
  mat22 m1 = {{-1, 2}, {3, 4}}, m3 = {{0,0},{0,0}}, m2;
    
  mat22_sub(m1, m1, m2);
  mu_assert("sub failed", mat22_equals(m2, m3));
  return 0;
}

static char* test_mat22_copy_v(void) {
  vec2 v1 = {1, 2}, v2;
    
  mat22_copy_v(v1, v2);
  mu_assert("copy_v failed", mat22_equals_v(v1, v2));
  return 0;
}

static char* test_mat22_copy(void) {
  mat22 m1 = {{1, 2}, {3, -4}}, m2;
    
  mat22_copy(m1, m2);
  mu_assert("copy failed", mat22_equals(m1, m2));
  return 0;
}




static char* all_tests(void) { 
  mu_run_test(test_mat22_mult); 
  mu_run_test(test_mat22_add); 
  mu_run_test(test_mat22_dot_vs); 
  mu_run_test(test_mat22_dot_vvt); 
  mu_run_test(test_mat22_dot_mv); 
  mu_run_test(test_mat22_dot_vtv); 
  mu_run_test(test_mat22_add_v); 
  mu_run_test(test_mat22_sub); 
  mu_run_test(test_mat22_copy_v); 
  mu_run_test(test_mat22_copy); 
  return 0;
}

int main() { 
  char *result = all_tests();
  if (result != 0) {
    printf("%s\n", result);
    return 1;
  }
  else {
    printf("ALL TESTS PASSED\n");
    return 0;
  }
}
