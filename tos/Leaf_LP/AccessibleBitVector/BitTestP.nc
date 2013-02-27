// -*- c -*-
#include "printf.h"

module BitTestP @safe()
{
  uses {
    interface Boot;
    interface AccessibleBitVector as Bs;
  }
}

implementation
{
  int tests_run=0;
  /** 
   * basic test of bitset
   *
   * @return 'char* NTS' error string 
   */
  static char* test_bitset(void) { 
    int i;

    call Bs.clearAll();
  
    for (i = 0; i < call Bs.size(); i++) { 
      /* printf("bs = %02x%02x\n", bs[0], bs[1]);  */
      mu_assert("bit shouldn't be set", call Bs.get(i) == 0);
      call Bs.set(i);
      mu_assert("bit should be set", call Bs.get(i));
    }

    for (i = call Bs.size()-1; i >= 0; i--) { 
      /* printf("bs = %02x%02x\n", bs[0], bs[1]);  */
      mu_assert("bit should be set", call Bs.get(i));
      call Bs.clear(i);
      mu_assert("bit shouldn't be set", call Bs.get(i) == 0);
    }


    return 0;
  }

  /** run all tests
   *
   * @return 'char* NTS' error string
   */
static char* all_tests(void) { 
  /* mu_run_test(test_bitset_iterator); */
  mu_run_test(test_bitset);

  return 0;
}

  event void Boot.booted()
  {
    char *result = all_tests();
    printf("Booted\n");
    if (result != 0) {
      printf("%s\n", result);
    }
    else {
      printf("ALL TESTS PASSED\n");
    }
    printf("Tests run: %d\n", tests_run);
    printfflush();
  }


  /*   uint8_t* bitArray; */
  /*   int bit; */
  /*   uint8_t arrayLength; */
  /*   int i=0; */
  /*   uint16_t call Bs.size(); */

  /*   call BVInit.init(); */
  /*   /\*set all bits to 1 *\/ */
  /*   call Bs.setAll(); */

  /*   //print array */
  /*   arrayLength=call Bs.getArrayLength(); */
  /*   bitArray=call Bs.getArray(); */


  /*   printfflush(); */
  /*   for(i=0;i<arrayLength;i++) */
  /*     { */
  /* 	//printf("BitArray[%u] = %i\n",i, bitArray[i]); */
  /*     } */
  /*   printfflush(); */
	
  /*   //set all bits to 1 */
  /*   call Bs.clearAll(); */

  /*   //print array */
  /*   arrayLength=call Bs.getArrayLength(); */
  /*   bitArray=call Bs.getArray(); */


  /*   for(i=0;i<arrayLength;i++) */
  /*     { */
  /* 	//printf("BitArray[%u] = %i\n",i, bitArray[i]); */
  /*     } */
  /*   printfflush(); */


  /*   bitArray=call Bs.getArray(); */

  /*   printf("Size= %i\n",i, (int)ARGGHH);  */
  /*   for (i = 0; i < ; i++) {  */
  /*     bit=call Bs.get(i); */
		
  /*     printf("Bit Should not be set[%u] = %i\n",i, bit); */
  /*     call Bs.set(i); */
  /*     bit=call Bs.get(i); */
  /*     printf("Bit Should be set[%u] = %i\n",i, bit); */
  /*   } */


  /*   call Bs.setAll(); */

  /*   for (i = ARGGHH-1; i >= 0; i--) {  */
  /*     bit=call Bs.get(i); */
  /*     printf("Bit Should be set[%u] = %i\n",i, bit); */
  /*     printfflush(); */
  /*     call Bs.clear(i); */
  /*     bit=call Bs.get(i); */
  /*     printf("Bit Should not be set[%u] = %i\n",i, bit); */
  /*     printfflush(); */
  /*   } */

  /* } */
}
