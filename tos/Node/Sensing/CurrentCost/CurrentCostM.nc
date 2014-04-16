/* -*- c -*-
   CurrentCostM.nc - Module to sample current cost electricity monitors.

   Copyright (C) 2011 Ross Wilkins

   This File is part of Cogent-House

   Cogent-House is free software: you can redistribute it and/or
   modify it under the terms of the GNU General Public License as
   published by the Free Software Foundation, either version 3 of the
   License, or (at your option) any later version.

   Cogent-House is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
   General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program. If not, see
   <http://www.gnu.org/licenses/>.



   ===================
   Current Cost Module
   ===================

   The module samples the current cost electricity monitor attached to the Telos Platforms
   UART0, the raw xml from the current cost monitor is parsed for the  ch0 value. The data is
   then averaged over the sensing period.


   :author: Ross Wilkins, James Brusey
   :email: ross.wilkins87@googlemail.com, james.brusey@gmail.com
   :date:  13/05/2011
*/

#ifdef DEBUG
#  include "printf.h"
#endif
#include "msp430usart.h"
#include "cc_struct.h"
#define MY_UINT16_MAX (65535U)

module CurrentCostM @safe()
{
  provides 
    {
      interface Read<float> as ReadWattage;
      interface SplitControl as CurrentCostControl;
    }
  uses
    {		
      interface Timer<TMilli> as TimeoutTimer;
      interface Timer<TMilli> as ResumeTimer;
      interface Timer<TMilli> as FirstByteTimer;
      interface LocalTime<TMilli>;
      interface UartStream as CurrentCostUartStream;
      interface SplitControl as UartControl;
      interface Leds;
    }
}
implementation
{
  enum { 
    TIMEOUT = 20,
    RESUME_PERIOD = 5120,
    FIRST_BYTE_TIMEOUT = 6144
  };
  
  
  /* shared variables */
  uint32_t totalWatts;
  uint32_t lastImpCount;
  uint16_t sampleCount, max_watts, min_watts;
  bool shared_reset_state = FALSE;

  /* non-shared */
  bool cc_stopped = TRUE;
  bool uart_suspended = FALSE;
  bool cc_start_requested = FALSE;
  bool cc_stop_requested = FALSE;

  //start and stop control methods

  /**************************************************************
   *
   * start and stop semantics obey the following rules:
   *
   * 1. when cc start is requested, uart will be started immediately
   * if it is currently stopped.
   *
   * 2. when cc stop is requested, stop request will be noted. If the
   * uart is suspended pending resume, then the resume timer is
   * cancelled and stopDone signalled.
   *
   * 3. when receiveByte times out, uart will be suspended.
   *
   * 4. when uart is suspended, stopDone will be signalled if stop has
   * been requested or a resume timer will be started.
   *
   **************************************************************/

  /** UartControl.startDone
   *
   *  triggered when uart has been started. This could be either
   *  because it was started when starting cc or it could be when the
   *  uart has been resumed.
   */
  event void UartControl.startDone(error_t error) { 
    if (error == SUCCESS) { 
      error = call CurrentCostUartStream.enableReceiveInterrupt();
      call FirstByteTimer.startOneShot(FIRST_BYTE_TIMEOUT);
      if (cc_start_requested) {
	cc_start_requested = FALSE;
	cc_stopped = FALSE;
	signal CurrentCostControl.startDone(error);
      }
    }
    else {
      // retry
      call UartControl.start();
    }

  }
      
  /** uartStop
   *
   *  turn off the interrupt and stop the uart.
   */
  error_t uartStop() {
    if (call CurrentCostUartStream.disableReceiveInterrupt() == SUCCESS &&
	call UartControl.stop() == SUCCESS)
      return SUCCESS;
    else
      return FAIL; // this should never happen
  }

  /** UartControl.stopDone
   *
   *  triggers when the uart has stopped. If the stop was requested
   *  externally, then signal their stopDone event too.
   */
  event void UartControl.stopDone(error_t error) {
    if (cc_stop_requested) {
      cc_stop_requested = FALSE;
      cc_stopped = TRUE;
      signal CurrentCostControl.stopDone(error);
    }
    else
      uart_suspended = TRUE;
  }

  command error_t CurrentCostControl.start()
  {
    if (!cc_stopped || cc_start_requested) 
      return EALREADY;
    cc_start_requested = TRUE;
    return call UartControl.start();
  }
	
  task void fakeStopDone() {
    cc_stopped = TRUE;
    signal CurrentCostControl.stopDone(SUCCESS);
  }

  command error_t CurrentCostControl.stop()
  {
    if (cc_stop_requested) 
      return EALREADY;

    if (uart_suspended) {
      /* uart is currently stopped so we can process immediately */
      uart_suspended = FALSE;
      call ResumeTimer.stop();
      post fakeStopDone();
    }
    else
      cc_stop_requested = TRUE;

    return SUCCESS;
  }

  task void readTask() 
  {
    uint32_t tw;
    uint16_t sc;
    //ccStruct results;
    
    atomic {
      tw = totalWatts;
      sc = sampleCount;
      totalWatts = 0;
      sampleCount = 0;
      max_watts = 0;
      min_watts = MY_UINT16_MAX;
      lastImpCount = 0;
    }

    if (sc != 0) {
      //results.average = ((float) tw) / sc;
      //results.max = (float) ma;
      //results.min = (float) mi;
      //results.kwh = lic / 1000.;
      signal ReadWattage.readDone(SUCCESS, ((float) tw) / sc);
    }
    else 
      signal ReadWattage.readDone(FAIL, 0);

#ifdef DEBUG
    printf("total = %lu, count = %u\n", tw, sc);
#endif

  }

  command error_t ReadWattage.read()
  {
    post readTask();
    return SUCCESS;
  }

/** 
 * Determine if a match for a particular string has been found by
 * keeping track of a simple state machine. This routine is called
 * once for each character in the string being searched in order.
 *
 * @param c the current character in the string being searched 
 * @param 'uint8_t* ONE state' a pointer to the current state, which
 *                             should be set to zero prior to the first call. 
 * @param 'char * NTS str' string to search for.
 * @return TRUE if a match has been found
 */
  bool match(char c, uint8_t * state, char* str) {
    if (*state < strlen(str) && c == str[*state]) {
      (*state)++;
      if (str[*state] == 0) {
	*state = 0;
	return TRUE;
      }
    } else {
      *state = 0;
    }
    return FALSE;
  }	

    
  typedef struct tag { 
    char * NTS stag, * NTS etag;
    uint8_t stag_i, etag_i;
    bool in_tag;
  } tag_t;

  void resetTag(tag_t *tag) { 
    tag->stag_i = tag->etag_i = 0;
    tag->in_tag = FALSE;
  }

  /** inTag
   */
  bool inTag(uint8_t byte, tag_t *tag) { 

    if (! tag->in_tag) { 
      if (match((char) byte, &(tag->stag_i), tag->stag))
	tag->in_tag = TRUE;
    }
    else {
      if (match((char) byte, &(tag->etag_i), tag->etag))
	tag->in_tag = FALSE;
    }
    return tag->in_tag;
  }

  enum {
    NUM_BEGIN = 0,
    NUM_IN = 1,
    NUM_END = 2,
    NUM_OUT = 3
  };
  uint8_t in_num = NUM_BEGIN;

  bool inNumber(uint8_t byte, uint32_t *value) {
    atomic {
      if (in_num == NUM_BEGIN) { 
	if (byte >= '0' && byte <= '9') {
	  in_num = NUM_IN;
	  *value = byte - '0';
	}
      }
      else if (in_num == NUM_IN) {
	if (byte >= '0' && byte <= '9') { 
	  *value = (*value) * 10 + (byte - '0');
	}
	else
	  in_num = NUM_END;
      }
      else if (in_num == NUM_END)
	in_num = NUM_OUT;
      return in_num;
    }
  }


  tag_t msg = {"<msg>", "</msg>", 0, 0, FALSE };
  tag_t ch1 = {"<ch1><watts>", "</watts></ch1>", 0, 0, FALSE };
  tag_t imp = {"<imp>", "</imp>", 0, 0, FALSE };
  uint32_t watts = 0;
  uint32_t impCount = 0;

  bool receiving_bytes = FALSE;

  event void TimeoutTimer.fired()
  {
    /* no bytes received for at least 1 second */
#ifdef DEBUG
    printf("timeout %u %u %d %u %u %d %u %u %d\n", 
	   ch1.stag_i,
	   ch1.etag_i,
	   ch1.in_tag,
	   imp.stag_i,
	   imp.etag_i,
	   imp.in_tag,
	   msg.stag_i,
	   msg.etag_i,
	   msg.in_tag);
    atomic printf("totalWatts=%lu, lastImpCount=%lu\n", totalWatts, lastImpCount);
#endif

    if (receiving_bytes) { 
      uartStop();
#ifdef DEBUG
      printf("Finished receiving at %lu\n", call LocalTime.get());
#endif
    }
    
    /* we can ignore non-atomic write problems here */
    if (! shared_reset_state) 
      shared_reset_state = TRUE;
    receiving_bytes = FALSE;
  }

  task void timerRestart()
  {
    if (! receiving_bytes) { 
      call ResumeTimer.startOneShot(RESUME_PERIOD);
#ifdef DEBUG
      printf("Started receiving at %lu\n", call LocalTime.get());
#endif
    }
    receiving_bytes = TRUE;
    call TimeoutTimer.startOneShot(TIMEOUT);
  }

  event void ResumeTimer.fired() 
  {
    /* if uart got turned off during a timeout, restart it */
    if (uart_suspended && !cc_stopped) { 
      uart_suspended = FALSE;
      call UartControl.start();
    }
  }

  event void FirstByteTimer.fired()
  {
    /* stop waiting for first byte */
    uartStop();
    /* restart after normal resume period */
    call ResumeTimer.startOneShot(RESUME_PERIOD);
  }

  async event void CurrentCostUartStream.receivedByte(uint8_t byte)
  {
    /* can ignore non-atomic write warnings on the basis that
       receivedByte only clears the flag and the timer only sets the
       flag.
    */
    if (shared_reset_state) {
      resetTag(&ch1);
      resetTag(&msg);
      in_num = NUM_BEGIN;
      shared_reset_state = FALSE;
    }

    post timerRestart();   

    if (inTag(byte, &msg)) { 
      if (inTag(byte, &ch1)) {
	if (inNumber(byte, &watts) == NUM_END) {
	  atomic { 
	    totalWatts += watts;
	    if (watts > max_watts) {
	      max_watts = watts;
	    }
	    if (min_watts > watts) {
	      min_watts = watts;
	    }
	    sampleCount ++;
	  }
	}
      }
      else if (inTag(byte, &imp)) { 
	if (inNumber(byte, &impCount) == NUM_END) {
	  atomic {
	    lastImpCount = impCount;
	  }
	}
      }
      else {
	in_num = NUM_BEGIN;
	watts = 0;
	impCount = 0;
      }
    }
  }

  async event void CurrentCostUartStream.receiveDone(uint8_t *buf, uint16_t len, error_t error){}
  async event void CurrentCostUartStream.sendDone(uint8_t* buf, uint16_t len, error_t error) { }
}

