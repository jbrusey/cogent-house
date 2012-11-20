/* -*- c -*-
   HeatMeterM.nc - Module to sense from a Minocal Combi Heat Meter

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
Minocal Combi Heat Meter Module
=====================================

Device: http://www.bellflowsystems.co.uk/minocal-compact-kwh-heat-meter-qn-1.5-1-2-reducing-kit-included-mid-approved.html

The module counts the number of interupts in a sample period from the Minocal Combi 
Heat Meter's energy, and volume pulse outputs. The Energy pulse output should be connected to GPIO3,
the volume pulse out put should be connected to GPIO2.

:author: Ross Wilkins
:email: ross.wilkins87@googlemail.com
:date:  06/01/2012
*/


module HeatMeterM
{
  provides {
    interface Read<hmStruct *> as ReadHeatMeter;
    interface SplitControl as HeatMeterControl;
  }
  uses {	
    interface HplMsp430GeneralIO as EnergyInput;
    interface HplMsp430Interrupt as EnergyInterrupt;	
    
    interface HplMsp430GeneralIO as VolumeInput;
    interface HplMsp430Interrupt as VolumeInterrupt;
  }
}
implementation
{
  int energyCount = 0;
  int volumeCount = 0;
  int sampleCount = 0;
  
  task void readTask() {
    uint32_t te;
    uint32_t tv;
    uint32_t sc;
    hmStruct results;
    
    atomic {
      te = energyCount;
      tv = volumeCount;
      sc = sampleCount;
      energyCount = 0;
      volumeCount = 0;
      sampleCount = 0;
    }
    results.energy = (float) te;
    results.volume = (float) tv * 100.0;
    signal ReadHeatMeter.readDone(SUCCESS, &results);
  }

  command error_t ReadHeatMeter.read() {
    post readTask();
    return SUCCESS;
  }

#ifdef DEBUG
  task void energyInterruptPrint(){
    printf("Energy Interrupt Fired\n");
    printfflush();
  }
#endif

  async event void EnergyInterrupt.fired() {
    //clear the interrupt pending flag then increment the count
    call EnergyInterrupt.clear();
    energyCount += 1;
    sampleCount += 1;
#ifdef DEBUG
    post energyInterruptPrint();
#endif
  }
  
#ifdef DEBUG
  task void volumeInterruptPrint(){
    printf("Volume  Interrupt Fired\n");
    printfflush();
  }
#endif
  async event void VolumeInterrupt.fired() {
    //clear the interrupt pending flag then increment the count
    call VolumeInterrupt.clear();  
    volumeCount += 1;
    sampleCount += 1;
#ifdef DEBUG
    post volumeInterruptPrint();
#endif
  }
  
  command error_t HeatMeterControl.start() {
    //Set up energy pulse
    atomic{
      call EnergyInterrupt.clear();
      call EnergyInterrupt.enable();
    }
    call EnergyInterrupt.edge(FALSE);
    call EnergyInput.makeInput();
    
    //Set up volume pulse
    atomic{
      call VolumeInterrupt.clear();
      call VolumeInterrupt.enable();
    }
    call VolumeInterrupt.edge(FALSE);  
    call VolumeInput.makeInput();
    signal HeatMeterControl.startDone(SUCCESS);
    return SUCCESS;
  }
  
  command error_t HeatMeterControl.stop() {
    signal HeatMeterControl.stopDone(SUCCESS);
    return SUCCESS;
  }
       
}

