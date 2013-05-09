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


module PulseReaderM
{
  provides {
    interface Read<float> as ReadPulse;
    interface SplitControl as PulseControl;
  }
  uses {	
    interface HplMsp430GeneralIO as EnergyInput;
    interface HplMsp430Interrupt as EnergyInterrupt;	
    interface Leds;
  }
}
implementation
{
  float energyCount = 0;
  
  task void readTask() {
    float te;
    atomic {
      te = energyCount;
      energyCount = 0;
    }

    signal ReadPulse.readDone(SUCCESS, te);
  }

  command error_t ReadPulse.read() {
    post readTask();
    return SUCCESS;
  }

  async event void EnergyInterrupt.fired() {
    //clear the interrupt pending flag then increment the count
    call EnergyInterrupt.clear();
#ifdef DEBUG
    call Leds.led2Toggle();
    call Leds.led1Toggle();
    call Leds.led0Toggle();
#endif
    energyCount += 1;
  }
  
  command error_t PulseControl.start() {
    //Set up energy pulse
    atomic{
      call EnergyInterrupt.clear();
      call EnergyInterrupt.enable();
    }
    call EnergyInterrupt.edge(FALSE);
    call EnergyInput.makeInput();
    signal PulseControl.startDone(SUCCESS);
    return SUCCESS;
  }
  
  command error_t PulseControl.stop() {
    signal PulseControl.stopDone(SUCCESS);
    return SUCCESS;
  }
       
}

