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
  CogentRootP.RadioControl -> Radio;
  CogentRootP.Leds -> LedsC;

  components new TimerMilliC() as RandomTimer;
  CogentRootP.RandomTimer -> RandomTimer;

  components RandomC;
  CogentRootP.Random -> RandomC;

  components new AMSenderC(AM_ACKMSG) as AckForwarder;
  CogentRootP.AckForwarder -> AckForwarder;

  components CrcC;
  CogentRootP.CRCCalc -> CrcC;

  components new QueueC(AckMsg*, RADIO_QUEUE_SIZE) as AckQueue;
  components new PoolC(message_t, RADIO_QUEUE_SIZE) as AckPool;
  CogentRootP.AckQueue -> AckQueue;
  CogentRootP.AckPool -> AckPool;

}
