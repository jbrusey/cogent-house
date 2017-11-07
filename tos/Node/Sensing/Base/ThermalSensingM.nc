/* -*- c -*-
   ThermalSensingM.nc - Module to sample temperature and humidity sensors.

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
   Thermal Sensing Module
   ===================

   The module samples the TelosB's on board temperature and humidity 
   sensors. The raw adc values are then converted in to real engineering 
   values.


   :author: Ross Wilkins
   :email: ross.wilkins87@googlemail.com
   :date:  05/01/2011
*/
#include "horner.h"

module ThermalSensingM @safe()
{
  provides 
    {
      interface Read<float> as ReadTemp;
      interface Read<float> as ReadHum;
    }
  uses
    {		
      interface Read<uint16_t> as GetTemp;
      interface Read<uint16_t> as GetHum;
    }
}
implementation
{

  float temp; //Temperature - deg c



  //will initially need to be read from config in next version 
  //Temp= 0.01x+-39.60
  float tempCoeffs[] = {-39.60, 0.01};

  //humidity=-0.0000028*x^2+0.0405*x-4
  float humCoeffs[] = {-4, 0.0405,-0.0000028};
	
  command error_t ReadTemp.read()
  {
    // TODO check that it is not necessary to post the split phase
    return call GetTemp.read();
  }

  command error_t ReadHum.read()
  {
    return call GetHum.read();
  }


  //Convert raw adc to temp
  event void GetTemp.readDone(error_t result, uint16_t data) {
    if (result == SUCCESS) {
      temp = horner(sizeof(tempCoeffs)/sizeof(float)-1, tempCoeffs, (float)data);
      signal ReadTemp.readDone(SUCCESS, temp);
    }
    else 
      signal ReadTemp.readDone(result, 0.);
	    
  }

  //Convert raw adc to hum
  event void GetHum.readDone(error_t result, uint16_t data) {
    if (result == SUCCESS) { 
      float hum;
      float humOffset;
      hum = horner(sizeof(humCoeffs)/sizeof(float)-1, humCoeffs, (float)data);
      humOffset = ((temp - 25) * (0.01 + 0.00008*data));
      hum = hum-humOffset;
      signal ReadHum.readDone(SUCCESS, hum);
    }
    else 
      signal ReadHum.readDone(result, 0.);
  }
}

