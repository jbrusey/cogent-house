// -*- c -*-

module BlinkStatusP
{
  uses {
    interface Timer<TMilli> as BlinkTimer;
    interface Leds;
  }
  provides {
    interface BlinkStatus;
  }

}
implementation {
  error_t flag = FAIL;
  uint8_t blink_state = 0;
  uint8_t blink_thrice_state = 0;

  uint8_t gray[] = { 0, 1, 3, 2, 6, 7, 5, 4 };


  command void BlinkStatus.start() { 
    //reset vars
    blink_state = 0;
    blink_thrice_state = 0;
    flag = FAIL;

    call BlinkTimer.startOneShot(512L); 
    /* start blinking to show that we are up and running */
  }

  command void BlinkStatus.setStatus(error_t val) { 
    flag = val;
  }

  command error_t BlinkStatus.getStatus() { 
    return flag;
  }


  ////////////////////////////////////////////////////////////
  // Produce a nice pattern on start-up
  //
  void blinkThrice(bool ok) {
    if (blink_thrice_state < 6) {
      blink_thrice_state++;
      call BlinkTimer.startOneShot(1024L);
      if (blink_thrice_state == 1) 
	call Leds.set(0);
      else if (ok)
	call Leds.led1Toggle(); /* green */
      else
	call Leds.led0Toggle(); /* red */
    }
    else 
      call Leds.set(0);
  }

  event void BlinkTimer.fired() { 
    if (flag == SUCCESS)
      blinkThrice(TRUE);
    else if (blink_state >= 2 * BLINK_SECONDS) { /* 60 seconds */
      blinkThrice(FALSE);
    }
    else { 
      blink_state++;
      call BlinkTimer.startOneShot(512L);
      call Leds.set(gray[blink_state % (sizeof gray / sizeof gray[0])]);
    }
  }
  

}
