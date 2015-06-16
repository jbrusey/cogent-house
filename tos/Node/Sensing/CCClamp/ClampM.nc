/* -*- c -*-
   ClampM.nc - Methods to sample current cost clamp sensor

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
Current cost clamp Module
===================

ClampM provides read method to read from a directly interfaced current cost clamp based on the code
by the Open Energy Monitoring Project at http://openenergymonitor.org/emon/
and https://github.com/openenergymonitor/EmonLib

:author: Ross Wilkins
:email: ross.wilkins87@googlemail.com
:date:  11th March 2013
*/

#include "clamp_struct.h"
#include "msp430usart.h"
#define MY_UINT16_MAX (65535U)

module ClampM
{      
  provides {
    interface Read<clampStruct *> as ReadClamp;
    interface SplitControl as ClampControl;
  }
  uses{		
    interface Read<uint16_t> as GetClamp;
    interface Timer<TMilli> as SenseTimer;
  }
}
implementation
{
  const float VREF = 3.3; // TODO: check this value
  const float MAXADC = 4095.0;
  const float ICAL = 111.1; 
  const int NUMBER_OF_SAMPLES = 1536; //2ms*1536=3secs
  const float HOUSE_VOLTAGE = 240.; //uk voltage
  const uint32_t SAMPLE_PERIOD = 6144.; //6 seconds same as current cost
  
  float lastSampleI = 0.0;
  float lastFilteredI = 0.0;
  
  float sumI;
  uint32_t totalWatts, sampleCount;
  float max_watts, min_watts;
  
  
  task void readClampTask(){ 
    uint32_t tw;
    uint16_t sc;
    float ma, mi;
    clampStruct results;
    
    atomic {
      tw = totalWatts;
      sc = sampleCount;
      ma = max_watts;
      mi = min_watts;
      totalWatts = 0;
      sampleCount = 0;
      max_watts = 0;
      min_watts = MY_UINT16_MAX;
    }
    
    //start read timer
    call SenseTimer.startPeriodic(SAMPLE_PERIOD);
    
    if (sc != 0) {
      results.average = ((float) tw) / sc;
      results.max = ma;
      results.min = mi;
      signal ReadClamp.readDone(SUCCESS, &results);
    }
    else 
      signal ReadClamp.readDone(FAIL, NULL);    
  }
	
  command error_t ReadClamp.read(){
    //stop read timer
    call SenseTimer.stop();
    post readClampTask();
    return SUCCESS;
  }
		
  //Convert raw adc to temp and add to current accumulator
  event void GetClamp.readDone(error_t result, uint16_t data) {
    float sqI;
    float filteredI;
    float sampleI=(data/MAXADC)*VREF;
    
    //Filter the current
    filteredI = 0.996*(lastFilteredI+sampleI-lastSampleI);
    
    //Square and sum value for RMS
    sqI = filteredI * filteredI;
    sumI += sqI;
    
    //reset previous states
    lastSampleI = sampleI;
    lastFilteredI = filteredI;
  }

  //calculate current wattage using rms method
  void calcWattage(){
    double Irms;
    double I_RATIO;
    float watts;
    int n;
    
    for (n = 0; n < NUMBER_OF_SAMPLES; n++){
      call GetClamp.read();
    }
    
    //calculate rms
    I_RATIO = ICAL *((VREF/1000.0) / 1023.0);
    Irms = I_RATIO * sqrtf(sumI / NUMBER_OF_SAMPLES); 
    
    //convert to wattage using p=iv where = uk volatage of 240
    watts = (Irms * HOUSE_VOLTAGE);
    
    //process stats
    totalWatts += watts;
    sampleCount += 1;
    if (watts < min_watts)
      min_watts = watts;
    if (watts > max_watts)
      max_watts = watts;
    
    //Reset accumulators
    sumI = 0;
  }
	
	
  event void SenseTimer.fired() {
    calcWattage();
  }
  
  command error_t ClampControl.start() {
    //Set up reading timer
    call SenseTimer.startPeriodic(SAMPLE_PERIOD);
    signal ClampControl.startDone(SUCCESS);
    return SUCCESS;
  }
  
  command error_t ClampControl.stop() {
    signal ClampControl.stopDone(SUCCESS);
    return SUCCESS;
  }
  
}
