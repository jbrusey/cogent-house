// -*- c -*-
#include "msp430usart.h"
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#include "Parser.h"
configuration TestParserAppC { }

implementation
{
  components MainC, TestParserC, LedsC;
  components new BigAsyncQueueC(uint8_t, MAX_CC_MSGLEN) as MsgQueue;
  components ParserC;
  components PrintfC;
  components SerialStartC;

  TestParserC.Boot -> MainC.Boot;
  
  TestParserC.MsgQueue -> MsgQueue;
  TestParserC.Parser -> ParserC;
  ParserC.MsgQueue -> MsgQueue;
  TestParserC.Leds -> LedsC;
}

