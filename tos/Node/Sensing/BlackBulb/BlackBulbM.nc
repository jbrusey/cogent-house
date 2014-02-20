/* BlackBulbM.nc - Methods to sample both CO2 and VOC sensors

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
Black Bulb Module
===================

BlackBulbM provides methods to read from the BlackBulb Module


:author: Ross Wilkins
:email: ross.wilkins87@googlemail.com
:date:  18th November 2013
*/


module BlackBulbM
{
	provides 
	{
		interface Read<float> as ReadBB;
	}
	uses
	{		
		interface Read<uint16_t> as GetBB;
	}
}
implementation
{
	const uint32_t DELAY_PERIOD=1024;
	const float vref=3.3;
	const float maxAdc=4096.0;

	task void readBBTask()
	{
		call GetBB.read();
	}


	command error_t ReadBB.read()
	{
		post readBBTask();
		return SUCCESS;
	}

	//Convert raw adc to temp
	event void GetBB.readDone(error_t result, uint16_t data) {	
		float voltage;
		voltage=(data/maxAdc)*vref;
		signal ReadBB.readDone(SUCCESS, voltage);
	}


}
