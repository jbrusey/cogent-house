/* -*- c -*-
   BatterySensingM.nc - Module to sample temperature and humidity sensors.

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
   Battery Sensing Module
   ===================

   The module samples the TelosB's on board battery sensors. 
   The raw adc values are then converted in to real engineering 
   values.


   :author: Ross Wilkins
   :email: ross.wilkins87@googlemail.com
   :date:  26/10/2011
*/


module BatterySensingM @safe()
{
  provides 
    {
      interface Read<float> as ReadBattery;
    }
  uses
    {		
      interface Read<uint16_t> as GetVoltage;
    }
}
implementation
{

	
  command error_t ReadBattery.read()
  {
    // TODO check that it is not necessary to post the split phase
    return call GetVoltage.read();
  }


  //Convert raw adc to temp
  event void GetVoltage.readDone(error_t result, uint16_t data) {
    if (result == SUCCESS) {

      signal ReadBattery.readDone(SUCCESS, (data/4096.0)*3);
    }
    else 
      signal ReadBattery.readDone(result, 0.);
	    
  }

}

