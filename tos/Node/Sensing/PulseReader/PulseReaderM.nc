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
:email: ross.wilkins87@googlemail.com
:date:  09/05/2013
*/


generic module PulseReaderM()
{
  provides {
    interface Read<float> as ReadPulse;
    interface SplitControl as PulseControl;
  }
  uses {	
    interface HplMsp430GeneralIO as Input;
    interface HplMsp430Interrupt as Interrupt;	
    interface Leds;
  }
}
implementation
{
  uint32_t Count = 0;
  
  task void readTask() {
    float te;
    atomic {
      te = (float) Count;
    }

    signal ReadPulse.readDone(SUCCESS, te);
  }

  command error_t ReadPulse.read() {
    post readTask();
    return SUCCESS;
  }

  async event void Interrupt.fired() {
    //clear the interrupt pending flag then increment the count
    call Interrupt.clear();
#ifdef DEBUG
    call Leds.led2Toggle();
#endif
    Count++;
  }
  
  command error_t PulseControl.start() {
    //Set up pulse
    atomic{
      call Interrupt.clear();
      call Interrupt.enable();
    }
    call Interrupt.edge(FALSE);
    call Input.makeInput();
    signal PulseControl.startDone(SUCCESS);
    return SUCCESS;
  }
  
  command error_t PulseControl.stop() {
    signal PulseControl.stopDone(SUCCESS);
    return SUCCESS;
  }
       
}

