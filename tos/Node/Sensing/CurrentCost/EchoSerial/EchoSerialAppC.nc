// -*- c -*-
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
configuration EchoSerialAppC { }

implementation
{
  components MainC, EchoSerialC, LedsC;
  components CurrentCostSerialC;
  components new BigAsyncQueueC(uint8_t, 1000) as ByteQueue;
  components PrintfC;
  components SerialStartC;

  EchoSerialC.Boot -> MainC.Boot;
  EchoSerialC.CurrentCostUartStream -> CurrentCostSerialC;
  EchoSerialC.CurrentCostControl -> CurrentCostSerialC;
  EchoSerialC.ByteQueue -> ByteQueue;
  EchoSerialC.Leds -> LedsC;
}

