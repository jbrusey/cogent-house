// -*- c -*-
#include "../Packets.h"
configuration CogentRootC {
  provides interface Intercept as RadioIntercept[am_id_t amid];
}
implementation
{
  components CogentRootP, MainC, LedsC;
  components SerialActiveMessageC as Serial;
  components ActiveMessageC as Radio;

  CogentRootP.Boot -> MainC;

  components new SerialAMReceiverC(AM_ACKMSG) as AckReceiver;
  CogentRootP.UartAckReceive -> AckReceiver;

  CogentRootP.SerialControl -> Serial;
  CogentRootP.UartSend -> Serial;
  CogentRootP.UartPacket -> Serial;
  CogentRootP.UartAMPacket -> Serial;

  CogentRootP.RadioControl -> Radio;
  CogentRootP.Leds -> LedsC;

  components CollectionC; 
  CogentRootP.CollectionControl -> CollectionC;
  CogentRootP.RootControl -> CollectionC;
  CogentRootP.CollectionPacket -> CollectionC;
  CogentRootP.CollectionReceive -> CollectionC.Receive;
  CogentRootP.RadioPacket -> CollectionC;
  
  RadioIntercept = CogentRootP.RadioIntercept;

  components DisseminationC;
  components new DisseminatorC(AckMsg, AM_ACKMSG);
  CogentRootP.DisseminationControl -> DisseminationC;
  CogentRootP.AckUpdate -> DisseminatorC;
  components CrcC;
  CogentRootP.CRCCalc -> CrcC;

  components new QueueC(message_t*, SERIAL_QUEUE_SIZE);
  components new PoolC(message_t, SERIAL_QUEUE_SIZE);
  CogentRootP.Queue -> QueueC;
  CogentRootP.Pool -> PoolC;
	
  components new TimerMilliC() as BlinkTimer;
  CogentRootP.BlinkTimer -> BlinkTimer;

  components new TimerMilliC() as AckTimeoutTimer;
  CogentRootP.AckTimeoutTimer ->  AckTimeoutTimer;

  /* error display */
  components new TimerMilliC() as ErrorDisplayTimer;
  components ErrorDisplayM;
  ErrorDisplayM.ErrorDisplayTimer -> ErrorDisplayTimer;
  ErrorDisplayM.Leds -> LedsC;
  CogentRootP.ErrorDisplayControl -> ErrorDisplayM.ErrorDisplayControl;
  CogentRootP.ErrorDisplay -> ErrorDisplayM.ErrorDisplay;
}
