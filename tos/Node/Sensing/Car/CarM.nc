module CarM
{
	provides 
	{
		interface Read<float> as ReadTempADC0;
		interface Read<float> as ReadTempADC1;
		interface Read<float> as ReadTempADC2;
		interface Read<float> as ReadTempADC3;
		interface Read<float> as ReadFlowADC1;
		interface Read<float> as ReadFlowADC3;
		interface Read<float> as ReadFlowADC7;
		interface Read<float> as ReadSolar;
		interface Read<float> as ReadSolar_ADC3;
		interface Read<float> as ReadBlackBulb;
		interface Read<float> as ReadCO2;
	}
	uses
	{
		interface Read<uint16_t> as GetTempADC0;
		interface Read<uint16_t> as GetTempADC1;
		interface Read<uint16_t> as GetTempADC2;
		interface Read<uint16_t> as GetTempADC3;
		interface Read<uint16_t> as GetFlowADC1;
		interface Read<uint16_t> as GetFlowADC3;
		interface Read<uint16_t> as GetFlowADC7;	
		interface Read<uint16_t> as GetSolar;
		interface Read<uint16_t> as GetSolar_ADC3;
		interface Read<uint16_t> as GetBlackBulb;
		interface Read<uint16_t> as GetCO2;
		interface HplMsp430GeneralIO as CO2On;
		interface Timer<TMilli> as WarmUpTimer;	
	}
}
implementation
{
	const uint32_t DELAY_PERIOD=0.;
	const float vref=2.5;
	const float maxAdc=4096.0;
	float SolarCoeffs[] = {0, 100};
	float CO2Coeffs[] = {-1250, 5000};
	float TempCoeffs[] = {-50, 100};
	float FlowCoeffs[] = {0, 1};
	float BlackBulbCoeffs[] = {0, 1};

	//Temp0
	task void readTemp0Task()
	{
		call GetTempADC0.read();
	}

	command error_t ReadTempADC0.read()
	{
		post readTemp0Task();
		return SUCCESS;
	}

	//Convert raw adc to temp
	event void GetTempADC0.readDone(error_t result, uint16_t data) {
		float voltage;
		float temp;
		voltage=(data/maxAdc)*vref;
		temp = horner(sizeof(TempCoeffs)/sizeof(float)-1, TempCoeffs, (float)voltage);
		signal ReadTempADC0.readDone(SUCCESS, temp);
	}

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


	//Temp3
	task void readTemp3Task()
	{
		call GetTempADC3.read();
	}

	command error_t ReadTempADC3.read()
	{
		post readTemp3Task();
		return SUCCESS;
	}

	//Convert raw adc to temp
	event void GetTempADC3.readDone(error_t result, uint16_t data) {
		float voltage;
		float temp;
		voltage=(data/maxAdc)*vref;
		temp = horner(sizeof(TempCoeffs)/sizeof(float)-1, TempCoeffs, (float)voltage);
		signal ReadTempADC3.readDone(SUCCESS, temp);
	}
	
	//Flow 1
	task void readFlow1Task()
	{
		call GetFlowADC1.read();
	}

	command error_t ReadFlowADC1.read()
	{
		post readFlow1Task();
		return SUCCESS;
	}

	//Convert raw adc to temp
	event void GetFlowADC1.readDone(error_t result, uint16_t data) {
		float voltage;
		float flow;
		voltage=(data/maxAdc)*vref;
		flow = horner(sizeof(FlowCoeffs)/sizeof(float)-1, FlowCoeffs, (float)voltage);
		signal ReadFlowADC1.readDone(SUCCESS, flow);
	}

	//Flow 3
	task void readFlow3Task()
	{
		call GetFlowADC3.read();
	}

	command error_t ReadFlowADC3.read()
	{
		post readFlow3Task();
		return SUCCESS;
	}

	//Convert raw adc to temp
	event void GetFlowADC3.readDone(error_t result, uint16_t data) {
		float voltage;
		float flow;
		voltage=(data/maxAdc)*vref;
		flow = horner(sizeof(FlowCoeffs)/sizeof(float)-1, FlowCoeffs, (float)voltage);
		signal ReadFlowADC3.readDone(SUCCESS, flow);
	}

	//Flow 7
	task void readFlow7Task()
	{
		call GetFlowADC7.read();
	}

	command error_t ReadFlowADC7.read()
	{
		post readFlow7Task();
		return SUCCESS;
	}

	//Convert raw adc to temp
	event void GetFlowADC7.readDone(error_t result, uint16_t data) {
		float voltage;
		float flow;
		voltage=(data/maxAdc)*vref;
		flow = horner(sizeof(FlowCoeffs)/sizeof(float)-1, FlowCoeffs, (float)voltage);
		signal ReadFlowADC7.readDone(SUCCESS, flow);
	}


	//SOLAR
	task void readSolarTask()
	{
		call GetSolar.read();
	}

	command error_t ReadSolar.read()
	{
		post readSolarTask();
		return SUCCESS;
	}

	//Convert raw adc to temp
	event void GetSolar.readDone(error_t result, uint16_t data) {
		float voltage;
		float Solar;
		voltage=(data/maxAdc)*vref;
		Solar = horner(sizeof(SolarCoeffs)/sizeof(float)-1, SolarCoeffs, (float)voltage);
		signal ReadSolar.readDone(SUCCESS, Solar);
	}
	
	//SOLAR (ADC 3)
	task void readSolar_ADC3Task()
	{
		call GetSolar_ADC3.read();
	}

	command error_t ReadSolar_ADC3.read()
	{
		post readSolar_ADC3Task();
		return SUCCESS;
	}

	//Convert raw adc to temp
	event void GetSolar_ADC3.readDone(error_t result, uint16_t data) {
		float voltage;
		float Solar;
		voltage=(data/maxAdc)*vref;
		Solar = horner(sizeof(SolarCoeffs)/sizeof(float)-1, SolarCoeffs, (float)voltage);
		signal ReadSolar_ADC3.readDone(SUCCESS, Solar);
	}
	
	// BLACK BULB
	task void readBlackBulbTask()
	{
		call GetBlackBulb.read();
	}

	command error_t ReadBlackBulb.read()
	{
		post readBlackBulbTask();
		return SUCCESS;
	}

	//Convert raw adc to temp
	event void GetBlackBulb.readDone(error_t result, uint16_t data) {
		float voltage;
		float BlackBulb;
		voltage=(data/maxAdc)*vref;
		BlackBulb = horner(sizeof(BlackBulbCoeffs)/sizeof(float)-1, BlackBulbCoeffs, (float)voltage);
		signal ReadBlackBulb.readDone(SUCCESS, BlackBulb);
	}

	//CO2

        task void readCO2Task()
	{
		//enable sensor - turn on GPIO2
		call CO2On.makeOutput();
		call CO2On.set();
		//let the sensor warmup
		call WarmUpTimer.startOneShot(DELAY_PERIOD);
	}

	event void WarmUpTimer.fired() {
		call GetCO2.read();
	}


        command error_t ReadCO2.read()
	{
		post readCO2Task();
		return SUCCESS;
	}


	//Convert raw adc to temp
	event void GetCO2.readDone(error_t result, uint16_t data) {
		float voltage;
		float CO2;
		voltage=(data/maxAdc)*vref;
		CO2 = horner(sizeof(CO2Coeffs)/sizeof(float)-1, CO2Coeffs, (float)voltage);
		signal ReadCO2.readDone(SUCCESS, CO2);
	}
}
