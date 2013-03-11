// -*- c -*-
#include "printf.h"

module PackStateTestP @safe()
{
  uses {
    interface Boot;
    interface PackState;
  }
}

implementation
{
  int tests_run=0;
 
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

  /** 
   * @return 'char * NTS' error 
   */ 
   static char* test_packstate1(void) { 

    packed_state_t ps;
    int pslen, i;
    

    call PackState.clear();
    call PackState.add(1, 25.5);
    call PackState.add(2, 1e-5);
    call PackState.add(7, 48.001);
    call PackState.add(8, 7.0);

    pslen = call PackState.pack(&ps);

    mu_assert("packed to wrong length", pslen == 4);
    
    mu_assert("4th item should be 7.0", ps.p[3] == 7.0);

    call PackState.unpack(&ps);
        
    mu_assert("wrong value1", call PackState.get(1) == 25.5);
    mu_assert("wrong value2", call PackState.get(2) == 1e-5);
    mu_assert("wrong value3", call PackState.get(7) == 48.001);
    mu_assert("wrong value4", call PackState.get(8) == 7.0);

    for (i = 0; i < SC_SIZE; i++) {
      if (call PackState.haskey(i)) {
	mu_assert("wrong key", i == 1 ||
		  i == 2 ||
		  i == 7 || 
		  i == 8);
      }
      else {
	mu_assert("missing key", !(i == 1 ||
				   i == 2 ||
				   i == 7 || 
				   i == 8));
      }
    }

    return 0;
    
  }

   /** 
    * @return 'char * NTS' error 
    */
  static char* all_tests(void) { 
    /* mu_run_test(test_bitset_iterator); */
    mu_run_test(test_packstate1); 
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
