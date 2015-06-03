// -*- c -*-

configuration BlinkStatusTestC
{}

implementation
{
  components MainC, BlinkStatusTestP;

  components PrintfC, SerialStartC;

  components BlinkStatusC;
  components new TimerMilliC() as TestTimer;
  components new TimerMilliC() as FailTimer;

  BlinkStatusTestP.Boot -> MainC.Boot;

  BlinkStatusTestP.BlinkStatus -> BlinkStatusC;
  BlinkStatusTestP.TestTimer -> TestTimer;
  BlinkStatusTestP.FailTimer -> FailTimer;
}
