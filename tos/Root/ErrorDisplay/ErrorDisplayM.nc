/* -*- c -*-
   ErrorDisplayM.nc - Module to display errors on the root node

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
   Error Display Module
   ===================

   As printf cannot be useed in conjunction with serial forwarder a method to display errors on the LEDS are provided


   :author: Ross Wilkins
   :email: ross.wilkins87@googlemail.com
   :date:  01/08/2013
*/


module ErrorDisplayM @safe()
{
  provides {
    interface ErrorDisplay;
    interface StdControl as ErrorDisplayControl;
  }
  uses {		
    interface Timer<TMilli> as ErrorDisplayTimer;
    interface Leds;
  }
}
implementation
{
  enum {
    ERROR_HISTORY_LEN = 8,
    ERROR_END_DELAY = 3
  };

  uint8_t errors[ERROR_HISTORY_LEN];
  bool error_blink_state = TRUE;
  uint8_t last_led_setting = 0;
  uint8_t error_read_ptr = 0;
  uint8_t error_write_ptr = 0;
  
  command void ErrorDisplay.add(uint8_t err)
  {
    // insert in next available pos
    errors[error_write_ptr] = err;
    error_write_ptr ++;
    error_write_ptr %= ERROR_HISTORY_LEN;
  }

  void resetErrors()
  {
    //initialise to 0
    int i;
    for ( i = 0; i < ERROR_HISTORY_LEN; i++ ){
      errors[ i ] = 0; /* set element at location i to 0 */
    }
    
    error_write_ptr = 0;
    error_blink_state = TRUE;
  }
  
  //error display
  event void ErrorDisplayTimer.fired() {
    if (error_blink_state == TRUE) {
      if (error_read_ptr < ERROR_HISTORY_LEN &&
	  errors[error_read_ptr] != last_led_setting) {
	call Leds.set(errors[error_read_ptr]);
	last_led_setting = errors[error_read_ptr];
      }
      
      error_read_ptr++;
      error_read_ptr %= ERROR_HISTORY_LEN + ERROR_END_DELAY;
      error_blink_state = FALSE;
    }
    else {
      if (last_led_setting != 0) {
	call Leds.set(0);
	last_led_setting = 0;
      }
      error_blink_state = TRUE;
    }
  }
 
 
  command error_t ErrorDisplayControl.start() {
    resetErrors();
    call ErrorDisplayTimer.startPeriodic(512L);
    return SUCCESS;
  }
  
  command error_t ErrorDisplayControl.stop() {
    call ErrorDisplayTimer.stop();
    return SUCCESS;
  }
}

