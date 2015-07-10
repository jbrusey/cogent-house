// -*- c -*-

generic module GIOSwitchM()
{
  provides {
    interface StdControl as SwitchControl;
  }
  uses {	
    interface HplMsp430GeneralIO as Switch;
#ifdef DEBUG
    interface Leds;
#endif
  }
}
implementation
{

  uint32_t users = 0;
  bool first=TRUE;

  command error_t SwitchControl.start() {
    if (first == TRUE) {
      call Switch.makeOutput();
      first=FALSE;
    }
    users++;
    call Switch.set();
#ifdef DEBUG
    call Leds.led1On();
    call Leds.led0Off();
    printf("On %u\n", users);
    printfflush();
#endif
    return SUCCESS;
  }
  
  command error_t SwitchControl.stop() {
    users--;
    if (users == 0) {
      call Switch.clr();
#ifdef DEBUG
      call Leds.led1Off();
      call Leds.led0On();
      printf("Off %u\n", users);
      printfflush();
#endif
    }
    return SUCCESS;
  }
       
}

