// -*- c -*-

module GIOSwitchTestP
{
  uses {
    interface Boot;
    interface StdControl as SwitchControl; 
    interface Timer<TMilli> as Timer; 
    interface LocalTime<TMilli>; 
  }
}

implementation
{

  enum {
    PERIOD = 2048
  };

  uint32_t count = 0;
  
  event void Boot.booted()
  {
    printf("Boot\n");
    printfflush();
    call Timer.startOneShot(PERIOD);
  }  
  
   event void Timer.fired() { 
     count++;
     printf("Expected Users %u\n", (count % 4));
     printfflush();
     if ((count % 4) == 0) {
       //Call stop on all 3 active sensors
       call SwitchControl.stop();
       call SwitchControl.stop();
       call SwitchControl.stop();
     }
     else 
       call SwitchControl.start();
     call Timer.startOneShot(PERIOD);
   }
  
}
