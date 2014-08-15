module WallHumM
{
	provides 
	{
		interface Read<float> as ReadWallHum;
	}
	uses
	{
		interface Read<uint16_t> as GetWallHum;
	}
}
implementation
{
	const float vref=2.5;
	const float maxAdc=4095.0;

	//Hum1
	task void readHumTask()
	{
		call GetWallHum.read();
	}

	command error_t ReadWallHum.read()
	{
		post readHumTask();
		return SUCCESS;
	}

	//Convert raw adc to Hum
	event void GetWallHum.readDone(error_t result, uint16_t data) {
		float voltage;
		voltage=(data/maxAdc)*vref;
		signal ReadWallHum.readDone(SUCCESS, voltage);
	}
}
