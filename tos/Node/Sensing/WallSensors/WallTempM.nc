module TempADCM
{
	provides 
	{
		interface Read<float> as ReadWallTemp;
	}
	uses
	{
		interface Read<uint16_t> as GetWallTemp;
	}
}
implementation
{
	const float vref=3.3;
	const float maxAdc=4096.0;

	//Temp1
	task void readTempTask()
	{
		call GetWallTemp.read();
	}

	command error_t ReadWallTemp.read()
	{
		post readTempTask();
		return SUCCESS;
	}

	//Convert raw adc to temp
	event void GetWallTemp.readDone(error_t result, uint16_t data) {
		float voltage;
		float temp;
		voltage=(data/maxAdc)*vref;
		signal ReadWallTemp.readDone(SUCCESS, voltage);
	}
}
