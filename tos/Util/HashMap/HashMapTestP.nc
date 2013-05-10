// -*- c -*-

#include "printf.h"

module HashMapTestP @safe()
{
  uses {
    interface Boot;
    interface Map as LittleMap;
  }
}

implementation
{
  int tests_run = 0;


  /** 
   * @return 'char * NTS' error 
   */ 
   static char* test_map1(void) { 

     uint16_t val1;

     call LittleMap.init();
     mu_assert("should be able to put initially", 
	       call LittleMap.put(200, 1));
     mu_assert("should find 200", 
	       call LittleMap.contains(200));
     if (call LittleMap.get(200, &val1)) {
       mu_assert("get of 200 should be 1", val1 == 1);
     }
     else mu_assert("get failed", FALSE);
     return 0;
   }

  /** 
   * @return 'char * NTS' error 
   */ 
   static char* test_map2(void) { 

     uint16_t val1;

     call LittleMap.init();
     mu_assert("should be able to put initially", 
	       call LittleMap.put(200, 1));
     mu_assert("should be able to put 202", 
	       call LittleMap.put(202, 2));
     mu_assert("should be able to overwrite 200", 
	       call LittleMap.put(200, 2));
     mu_assert("should find 200", 
	       call LittleMap.contains(200));
     mu_assert("should not find 201", 
	       !call LittleMap.contains(201));
     mu_assert("should not find 301", 
	       !call LittleMap.contains(301));

     if (call LittleMap.get(200, &val1)) {
       mu_assert("get of 200 should be 2", val1 == 2);
     }
     else mu_assert("get failed", FALSE);
     return 0;
   }

  /** 
   * @return 'char * NTS' error 
   */ 
   static char* test_map3(void) { 

     uint16_t val1;

     call LittleMap.init();
     mu_assert("should be able to put initially", 
	       call LittleMap.put(200, 1));
     // with size = 101 and a simple hash, 301 will collide
     mu_assert("should be able to put 301", 
	       call LittleMap.put(301, 2));
     

     if (call LittleMap.get(200, &val1)) {
       mu_assert("get of 200 should be 1", val1 == 1);
     }
     else mu_assert("get failed", FALSE);


     if (call LittleMap.get(301, &val1)) {
       mu_assert("get of 200 should be 2", val1 == 2);
     }
     else mu_assert("get failed", FALSE);
     return 0;
   }

  /** 
   * @return 'char * NTS' error 
   */ 
   static char* test_map4(void) { 

     uint16_t i;

     call LittleMap.init();

     for (i = 0; i < 101; i++) {
       mu_assert("should be able to use put", 
		 call LittleMap.put(i, i));
     }

     mu_assert("should overflow",
	       !call LittleMap.put(102, 102));
     return 0;
   }


     


   /** 
    * @return 'char * NTS' error 
    */
  static char* all_tests(void) { 
    mu_run_test(test_map1); 
    mu_run_test(test_map2); 
    mu_run_test(test_map3); 
    mu_run_test(test_map4); 
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
