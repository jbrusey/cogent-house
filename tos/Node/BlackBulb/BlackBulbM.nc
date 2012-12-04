module BlackBulbM
{
	provides 
	{
		interface Read<float> as ReadTemp;
	}
	uses
	{
		interface Read<uint16_t> as GetTemp;
	}
}
implementation
{
	const float vref=3.3;
	const float maxAdc=4096.0;
	float BlackBulbCoeffs[] = {0, 1};

	//Temp1
	task void readTempTask()
	{
		call GetTemp.read();
	}

	command error_t ReadTemp.read()
	{
		post readTempTask();
		return SUCCESS;
	}


	//Convert raw adc to temp
	event void GetTemp.readDone(error_t result, uint16_t data) {
		float voltage;
		float temp;

		voltage=(data/maxAdc)*vref;
		temp = horner(sizeof(BlackBulbCoeffs)/sizeof(float)-1, BlackBulbCoeffs, (float)voltage);
		signal ReadTemp.readDone(SUCCESS, temp);
	}


}
