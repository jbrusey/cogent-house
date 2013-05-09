// -*- c -*-
#include "printf.h"

module PackStateTestP @safe()
{
  uses {
    interface Boot;
    interface PackState;
    interface Leds;
  }
}

implementation
{
  int tests_run=0;
 

  /** 
   * @return 'char * NTS' error 
   */ 
  static char* test_packstate1(void) { 

    packed_state_t ps;
    int pslen, i;
    

    call PackState.clear();
    mu_assert("fail from add", call PackState.add(1, 25.5) == SUCCESS);
    mu_assert("fail from add", call PackState.add(2, 1e-5) == SUCCESS);
    mu_assert("fail from add", call PackState.add(7, 48.001) == SUCCESS);
    mu_assert("fail from add", call PackState.add(8, 7.0) == SUCCESS);

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

  /** check that change to packstate to make packed version have a
      smaller limit works ok */
  static char * test_packstate2(void) { 
    packed_state_t ps;
    int pslen, i;
    int sc_list[] = {10, 2, 7, 8, 9, 1};
    float scv_list[] = {25.5f, 1e-5f, 48.001f, 7.0f, 9.0f, 10.0f};

    mu_assert("wrong length scv", sizeof scv_list / sizeof (float) == 
	      sizeof sc_list / sizeof (int));

    call PackState.clear();
    for (i = 0; i < sizeof sc_list / sizeof (int); i++) { 
      if (i < SC_PACKED_SIZE) 
	mu_assert("couldn't add", 
		  call PackState.add(sc_list[i], scv_list[i]) == SUCCESS);
      else
	mu_assert("could add but shouldn't!", 
		  call PackState.add(sc_list[i], scv_list[i]) == FAIL);
    }

    pslen = call PackState.pack(&ps);
    mu_assert("ps len exceeds limit", pslen <= SC_PACKED_SIZE);

    mu_assert("1st item should be 1e-5", ps.p[0] == scv_list[1]);

    call PackState.unpack(&ps);
        
    mu_assert("wrong value2", call PackState.get(2) == 1e-5f);
    mu_assert("wrong value3", call PackState.get(7) == 48.001f);
    mu_assert("wrong value4", call PackState.get(8) == 7.0f);
    mu_assert("wrong value4", call PackState.get(9) == 9.0f);
    mu_assert("wrong value4", call PackState.get(10) == 25.5f);
    
    for (i = 0; i < SC_SIZE; i++) {
      if (call PackState.haskey(i)) {
	mu_assert("wrong key", i == 10 ||
		  i == 2 ||
		  i == 7 || 
		  i == 8 || 
		  i == 9);
      }
      else {
	mu_assert("missing key", !(i == 10 ||
				   i == 2 ||
				   i == 7 || 
				   i == 8 ||
				   i == 9));
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
    mu_run_test(test_packstate2); 
    return 0;
  }


  event void Boot.booted()
  {
    char *result = all_tests();
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
