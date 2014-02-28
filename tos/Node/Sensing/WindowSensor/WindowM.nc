/* WindowM.nc - Methods to sample the window sensor

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
Window Sensor Module
===================

WindowM provides methods ReadWindow samples and returns the window sensor adc.

:author: Ross Wilkins
:email: ross.wilkins87@googlemail.com
:date:  14th October 2013
*/





module WindowM
{
	provides 
	{
		interface Read<float> as ReadWindow;
	}
	uses
	{		
		interface Read<uint16_t> as GetWindow;
	}
}
implementation
{
	task void readWindowTask()
	{
        	call GetWindow.read();
	}


	command error_t ReadWindow.read()
	{
		post readWindowTask();
		return SUCCESS;
	}




	#ifdef DEBUG
	void printfFloat(float toBePrinted) {
		uint32_t fi, f0, f1, f2;
		char c;
		float f = toBePrinted;

		if (f<0){
			c = '-'; f = -f;
		} else {
			c = ' ';
		}

		// integer portion.
		fi = (uint32_t) f;

		// decimal portion...get index for up to 3 decimal places.
		f = f - ((float) fi);
		f0 = f*10;   f0 %= 10;
		f1 = f*100;  f1 %= 10;
		f2 = f*1000; f2 %= 10;
		printf("%c%ld.%d%d%d\n", c, fi, (uint8_t) f0, (uint8_t) f1, (uint8_t) f2);
	}
	#endif

	//Convert raw adc to temp
	event void GetWindow.readDone(error_t result, uint16_t data) {
	        float open;
	        if (data >= 2048)
	                open=1;
                else
                        open=0;
		signal ReadWindow.readDone(SUCCESS, open);
	}


}
