// -*- c -*-
#include "../Packets.h"
#include <stdio.h>
#include <stdint.h>
#ifdef DEBUG
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#endif 

configuration CogentHouseC {}
implementation
{
  components CogentHouseP, ActiveMessageC, MainC, LedsC, ActiveMessageC as Radio;
#ifdef DEBUG
  components PrintfC;
  components SerialStartC;
#endif
	
  //import timers
  components new TimerMilliC() as BlinkTimer;
  components new AMReceiverC(AM_STATEMSG) as StateReceiver;
  components new AMSenderC(AM_STATEMSG) as StateForwarder;
  components new AMReceiverC(AM_ACKMSG) as AckReceiver;
  components new AMSenderC(AM_ACKMSG) as AckForwarder;
  components new AMReceiverC(AM_BNMSG) as BNReceiver;
  components new AMSenderC(AM_BNMSG) as BNForwarder;

  CogentHouseP.Boot -> MainC.Boot;
  CogentHouseP.StateReceiver -> StateReceiver;
  CogentHouseP.StateForwarder -> StateForwarder;
  CogentHouseP.AckForwarder -> AckForwarder;
  CogentHouseP.AckReceiver -> AckReceiver;
  CogentHouseP.BNReceiver -> BNReceiver;
  CogentHouseP.BNForwarder -> BNForwarder;

  CogentHouseP.BlinkTimer -> BlinkTimer;
  CogentHouseP.Leds -> LedsC;
  CogentHouseP.RadioControl -> ActiveMessageC;

  components HilTimerMilliC;
	
  CogentHouseP.LocalTime -> HilTimerMilliC;

  //Queues and Pools for forwarding
  components new QueueC(StateMsg*, RADIO_QUEUE_SIZE) as SMQueue;
  components new PoolC(message_t, RADIO_QUEUE_SIZE) as SMPool;
  CogentHouseP.SMQueue -> SMQueue;
  CogentHouseP.SMPool -> SMPool;

  components new QueueC(StateMsg*, RADIO_QUEUE_SIZE) as BNQueue;
  components new PoolC(message_t, RADIO_QUEUE_SIZE) as BNPool;
  CogentHouseP.BNQueue -> BNQueue;
  CogentHouseP.BNPool -> BNPool;

  components new QueueC(AckMsg*, RADIO_QUEUE_SIZE) as ACKQueue;
  components new PoolC(message_t, RADIO_QUEUE_SIZE) as ACKPool;
  CogentHouseP.ACKQueue -> ACKQueue;
  CogentHouseP.ACKPool -> ACKPool;

}
