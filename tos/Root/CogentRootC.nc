// -*- c -*-
#include "../Packets.h"
configuration CogentRootC { }
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


  components new AMSenderC(AM_ACKMSG) as AckForwarder;
  CogentRootP.AckForwarder -> AckForwarder;
  CogentRootP.Packet -> AckForwarder;
  components CrcC;
  CogentRootP.CRCCalc -> CrcC;

  components new QueueC(message_t*, RADIO_QUEUE_SIZE) as DataQueue;
  components new PoolC(message_t, RADIO_QUEUE_SIZE) as DataPool;
  CogentRootP.DataQueue -> DataQueue;
  CogentRootP.DataPool -> DataPool;

  components new QueueC(AckMsg_t*, RADIO_QUEUE_SIZE) as AckQueue;
  components new PoolC(message_t, RADIO_QUEUE_SIZE) as AckPool;
  CogentRootP.AckQueue -> AckQueue;
  CogentRootP.AckPool -> AckPool;
	
  components new TimerMilliC() as BlinkTimer;
  CogentRootP.BlinkTimer -> BlinkTimer;
}
