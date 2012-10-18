module WindowSensorM
{
	provides 
	{
		interface Read<float> as ReadTempADC1;
		interface Read<float> as ReadTempADC2;
	}
	uses
	{
		interface Read<uint16_t> as GetTempADC1;
		interface Read<uint16_t> as GetTempADC2;
	}
}
implementation
{
	const float vref=3.3;
	const float maxAdc=4096.0;
	//temp=100x-50
	float TempCoeffs[] = {-50,100};

	//Temp1
	task void readTemp1Task()
	{
		call GetTempADC1.read();
	}

	command error_t ReadTempADC1.read()
	{
		post readTemp1Task();
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
	event void GetTempADC1.readDone(error_t result, uint16_t data) {
		float voltage;
		float temp;
    	#ifdef DEBUG
		float tempa;
		#endif
		voltage=(data/maxAdc)*vref;
		temp = horner(sizeof(TempCoeffs)/sizeof(float)-1, TempCoeffs, (float)voltage);
		
		#ifdef DEBUG
		printf("W1 voltage: ");
		printfFloat(voltage);
        printf("Temp: ");
		printfFloat(temp);
		printf("Temp2: ");
		tempa=(voltage*214.8803763)-189.5755272;
		printfFloat(tempa);
		printfflush();
		#endif
		signal ReadTempADC1.readDone(SUCCESS, temp);
	}

	//Temp2
	task void readTemp2Task()
	{
		call GetTempADC2.read();
	}

	command error_t ReadTempADC2.read()
	{
		post readTemp2Task();
		return SUCCESS;
	}

	//Convert raw adc to temp
	event void GetTempADC2.readDone(error_t result, uint16_t data) {
		float voltage;
		float temp;
		voltage=(data/maxAdc)*vref;
		temp = horner(sizeof(TempCoeffs)/sizeof(float)-1, TempCoeffs, (float)voltage);
		signal ReadTempADC2.readDone(SUCCESS, temp);
	}
}
