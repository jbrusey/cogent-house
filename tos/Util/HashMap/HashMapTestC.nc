#include "../minunit.h"
#include "printf.h"

configuration HashMapTestC {}

implementation
{
  components MainC, HashMapTestP;
  components new HashMapC(101) as LittleMap;
  // components new HashMap(509) as BigMap;

  components PrintfC;
  components SerialStartC;

  HashMapTestP.Boot -> MainC.Boot;
  HashMapTestP.LittleMap -> LittleMap;
  //HashMapTestP.BigMap -> BigMap;
}
