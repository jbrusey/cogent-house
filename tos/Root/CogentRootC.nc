// -*- c -*-
#include "../Node/Packets.h"
configuration CogentRootC { }
implementation
{
  components CogentRootP, MainC, LedsC;
  components SerialActiveMessageC as Serial;
  components ActiveMessageC as Radio;
  components new SerialAMReceiverC(AM_CONFIGMSG) as SettingsReceiver;

  CogentRootP.Boot -> MainC;

  CogentRootP.SerialControl -> Serial;
  CogentRootP.UartSend -> Serial;
  CogentRootP.UartPacket -> Serial;
  CogentRootP.UartAMPacket -> Serial;
  CogentRootP.UartSettingsReceive -> SettingsReceiver;

  CogentRootP.RadioControl -> Radio;

#ifdef LOW_POWER_LISTENING
  CogentRootP.LowPowerListening -> Radio;
#endif
  CogentRootP.Leds -> LedsC;

  components CollectionC; 
  CogentRootP.CollectionControl -> CollectionC;
  CogentRootP.RootControl -> CollectionC;
  CogentRootP.CollectionPacket -> CollectionC;
  CogentRootP.CollectionReceive -> CollectionC.Receive;
  CogentRootP.RadioPacket -> CollectionC;
#ifdef DISSEMINATION
  components DisseminationC;
  components new DisseminatorC(ConfigMsg, DIS_SETTINGS);
  CogentRootP.DisseminationControl -> DisseminationC;
  CogentRootP.SettingsUpdate -> DisseminatorC;
#endif

  components new QueueC(message_t*, SERIAL_QUEUE_SIZE);
  components new PoolC(message_t, SERIAL_QUEUE_SIZE);
  CogentRootP.Queue -> QueueC;
  CogentRootP.Pool -> PoolC;
	
  components new TimerMilliC() as BlinkTimer;
  CogentRootP.BlinkTimer -> BlinkTimer;

}
