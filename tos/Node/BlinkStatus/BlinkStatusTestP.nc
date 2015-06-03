// -*- c -*-

module BlinkStatusTestP
{
  uses {
    interface Boot;
    interface BlinkStatus;
    interface Timer<TMilli> as TestTimer;
    interface Timer<TMilli> as FailTimer;
  }
}

implementation
{

  event void Boot.booted()
  {
    call BlinkStatus.start();
    call TestTimer.startOneShot(1024 * 10);
  }

  event void TestTimer.fired() {
    call BlinkStatus.setStatus(SUCCESS);
    call FailTimer.startOneShot(1024 * 7);
  }

  event void FailTimer.fired() {
    call BlinkStatus.start();
  }

}
