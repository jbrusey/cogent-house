module TempADCM
{
	provides 
	{
		interface Read<float> as ReadTempADC1;
	}
	uses
	{
		interface Read<uint16_t> as GetTempADC1;
	}
}
implementation
{
	const float vref=3.3;
	const float maxAdc=4096.0;
	//temp=100x-50
	float TempCoeffs[] = {-50, 100};

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

	//Convert raw adc to temp
	event void GetTempADC1.readDone(error_t result, uint16_t data) {
		float voltage;
		float temp;
		voltage=(data/maxAdc)*vref;
		temp = horner(sizeof(TempCoeffs)/sizeof(float)-1, TempCoeffs, (float)voltage);
		signal ReadTempADC1.readDone(SUCCESS, temp);
	}
}
