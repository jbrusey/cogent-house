// -*- c -*-
#include "../../Packets.h"
configuration TestUARTC {
}
implementation
{
  components TestUARTP, MainC, LedsC;
  components SerialActiveMessageC as Serial;
  
  TestUARTP.Boot -> MainC;

  TestUARTP.SerialControl -> Serial;
  TestUARTP.UartSend -> Serial;
  TestUARTP.UartPacket -> Serial;
  TestUARTP.UartAMPacket -> Serial;

  TestUARTP.Leds -> LedsC;
  
  components new QueueC(message_t*, SERIAL_QUEUE_SIZE);
  components new PoolC(message_t, SERIAL_QUEUE_SIZE);
  TestUARTP.Queue -> QueueC;
  TestUARTP.Pool -> PoolC;
  
  components new TimerMilliC() as SendTimer;
  TestUARTP.SendTimer -> SendTimer;

  /* error display */
  components new TimerMilliC() as ErrorDisplayTimer;
  components ErrorDisplayM;
  ErrorDisplayM.ErrorDisplayTimer -> ErrorDisplayTimer;
  ErrorDisplayM.Leds -> LedsC;
  TestUARTP.ErrorDisplayControl -> ErrorDisplayM.ErrorDisplayControl;
  TestUARTP.ErrorDisplay -> ErrorDisplayM.ErrorDisplay;
}

