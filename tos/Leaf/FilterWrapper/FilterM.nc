// -*- c -*-
#include "mat22.h"
#define HIGH_COVARIANCE 1e20

/* -*- c -*-
   KalmanM.nc - Wrapper to kalman filter

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
   Filter Wrapper Module
   ===================




   :author: Ross Wilkins
   :email: ross.wilkins87@googlemail.com
   :date:  05/01/2011
*/
#include "Filter.h"

generic module FilterM() @safe() {
  provides 
    {
      interface Read<FilterState *>;
    }
  uses
    {		
      interface Read<float> as GetSensorValue;
      interface Filter;
      interface LocalTime<TMilli>;
    }
}
implementation
{
	
  FilterState currentState;

  command error_t Read.read()
  {
    return call GetSensorValue.read();
  }

  event void GetSensorValue.readDone(error_t result, float data) {
    float v[2];
    uint32_t time;
    //get local time
    time = call LocalTime.get();
    currentState.z = data;

    call Filter.filter(data, time, v);
    currentState.time = time;
    currentState.x = v[0];
    currentState.dx = v[1];
    signal Read.readDone(SUCCESS, &currentState);	    
  }
	
	
}
