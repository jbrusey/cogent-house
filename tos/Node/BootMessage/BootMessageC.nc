// -*- c -*-
configuration BootMessageC { 
  provides interface BootMessage;
  uses interface Send as BootSender;
}

implementation
{
  components new TimerMilliC() as BootSendTimeOutTimer;
  components BootMessageP;
#ifdef DEBUG
  components HilTimerMilliC;
  BootMessageP.LocalTime ->HilTimerMilliC;
#endif

  BootMessageP.BootSendTimeOutTimer -> BootSendTimeOutTimer;
  BootMessageP.BootSender = BootSender;
  BootMessageP.BootMessage = BootMessage;
}

