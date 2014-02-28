/* -*- c -*-
   PulseReaderM.nc - Module to sense from a pulse output

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



=====================================
Pulse Reader Module
=====================================

The module counts the number of interupts in a sample period from the wired in GPIO port.

:author: Ross Wilkins
:author: James Brusey
:email: ross.wilkins87@googlemail.com
:date:  09/05/2013
*/


generic module PulseReaderM()
{
  provides {
    interface Read<float> as ReadPulse;
    interface StdControl as PulseControl;
  }
  uses {	
    interface HplMsp430GeneralIO as Input;
    interface HplMsp430Interrupt as Interrupt;	
    interface Alarm<TMilli, uint32_t>;
#ifdef DEBUG
    interface Leds;
#endif
  }
}
implementation
{
  enum { 
    DEBOUNCE_TIME = 100
  };

  uint32_t Count = 0;
  bool in_debounce = FALSE;
  
  task void readTask() {
    uint32_t te;
    atomic 
      te = Count;

    signal ReadPulse.readDone(SUCCESS, (float) te);
  }

  command error_t ReadPulse.read() {
    post readTask();
    return SUCCESS;
  }

  async event void Interrupt.fired() {
    bool my_in_debounce;
    my_in_debounce = in_debounce;
    in_debounce = TRUE;

    atomic 
      call Interrupt.clear();
    if (! my_in_debounce) { 
      atomic 
	Count++;
#ifdef DEBUG
      call Leds.led2On();
#endif
      call Alarm.start(DEBOUNCE_TIME);
    }
  }

  async event void Alarm.fired() {
    atomic 
      in_debounce = FALSE;
#ifdef DEBUG
    call Leds.led2Off();
#endif
  }

  command error_t PulseControl.start() {
    //Set up pulse
    atomic 
      call Interrupt.clear();
    call Interrupt.edge(FALSE);
    call Input.makeInput();
    atomic
      call Interrupt.enable();
    return SUCCESS;
  }
  
  command error_t PulseControl.stop() {
    return SUCCESS;
  }
       
}

