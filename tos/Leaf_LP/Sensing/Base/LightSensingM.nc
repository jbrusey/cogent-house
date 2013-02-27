/* -*- c -*-
   Thermalsensingm.nc - Module to sample LightTSR and LightPAR sensors.

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
Light Sensing Module
===================

The module samples the TelosB's on board LightTSR and LightPAR 
sensors. The raw adc values are then converted in to real engineering 
values.


:author: Ross Wilkins
:email: ross.wilkins87@googlemail.com
:date:  05/01/2011
*/


module LightSensingM
{
	provides 
	{
	    interface Read<uint16_t> as ReadPAR;
	    interface Read<uint16_t> as ReadTSR;
	}
	uses
	{		
		interface Read<uint16_t> as GetPAR;
		interface Read<uint16_t> as GetTSR;
	}
}
implementation
{

	//will initially need to be read from config in next version 
	//par=(int)3.662109375*data;
	float parCoeffs[] = {0, 3.662109375};

	//tsr=(int)0.3662109375*data;
	float tsrCoeffs[] = {0, 0.3662109375};
	task void readPARTask()
	{
		//get temp
		call GetPAR.read();
	}

	task void readTSRTask()
	{
		//get temp
		call GetTSR.read();
	}


	command error_t ReadPAR.read()
	{
		post readPARTask();
		return SUCCESS;
	}

	command error_t ReadTSR.read()
	{
		post readTSRTask();
		return SUCCESS;
	}

	//Convert raw adc to temp
	event void GetPAR.readDone(error_t result, uint16_t data) {	
		int par;
		par=horner(sizeof(parCoeffs)/sizeof(float)-1,parCoeffs,(float)data);
		signal ReadPAR.readDone(SUCCESS, par);
	}

	//Convert raw adc to temp
	event void GetTSR.readDone(error_t result, uint16_t data) {	
		int tsr;
		tsr=horner(sizeof(tsrCoeffs)/sizeof(float)-1,tsrCoeffs,(float)data);
		signal ReadTSR.readDone(SUCCESS, tsr);
	}
}

