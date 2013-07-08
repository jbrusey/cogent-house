/* ClampM.nc - Methods to sample current cost clamp sensor

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

ClampM provides read method to read from a directly interfaced current cost clamp


:author: Ross Wilkins
:email: ross.wilkins87@googlemail.com
:date:  6th January 2011
*/
module ClampM
{
	provides 
	{
		interface Read<float> as ReadClamp;
	}
	uses
	{		
		interface Read<uint16_t> as GetClamp;
	}
}
implementation
{
	const float vref=3.3;
	const float maxAdc=4096.0;

	// TO-DO add conversion coeffs here - (c,x,x2,x3...)
	float clampCoeffs[] = {-1250, 5000};
	

	task void readClampTask()
	{
		call GetClamp.read();
	}


	command error_t ReadClamp.read()
	{
		post readClampTask();
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
	event void GetClamp.readDone(error_t result, uint16_t data) {
		float voltage;
		float watts;
		voltage=(data/maxAdc)*vref;
		watts = horner(sizeof(clampCoeffs)/sizeof(float)-1, clampCoeffs, (float)voltage);

		#ifdef DEBUG
		printf("Clamp adc: ");
		printf("%u",data);
		printf("Clamp voltage: ");
		printfFloat(voltage);
		printf("House wattage: ");
		printfFloat(watts);
		printf("\n");
		printfflush();
		#endif

		signal ReadClamp.readDone(SUCCESS, watts);
	}

}
