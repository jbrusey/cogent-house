// -*- c -*- 
module ExposureC @safe()
{
  provides interface Exposure<float*>[uint8_t id];
  uses interface Read<float> as GetSensorValue[uint8_t id];
}
implementation
{
  uint32_t *bandCount[RS_SIZE];
  float *bandPct[RS_SIZE];
  float *bandLimit[RS_SIZE];
  float gamma[RS_SIZE];
  uint8_t num_bands[RS_SIZE];

  //find in which band a value falls.
  uint8_t findBand(float k, float* bands, uint8_t id)
  {
    uint8_t x;
    
    for ( x = 0; x < (num_bands[id]); x++ ) {
      if (k <= bandLimit[id][x]){
	return x;
      }
    }
    return num_bands[id]-1;
  }

  command void Exposure.init[uint8_t id](uint8_t nb, uint8_t raw_sensor, float g){
    int i;
    uint32_t count[nb];
    float pct[nb];

    gamma[id] = g;
    num_bands[id] = nb;

    //initialise bandCounts and pct
    
    //initialis bandLimits
    if (raw_sensor == RS_TEMPERATURE)
      bandLimit[id] = tBands;
    else if (raw_sensor == RS_HUMIDITY)
      bandLimit[id] = hBands;
    else if (raw_sensor == RS_CO2)
      bandLimit[id] = cBands;
    else if (raw_sensor == RS_VOC)
      bandLimit[id] = vBands;
    else if (raw_sensor == RS_AQ)
      bandLimit[id] = aBands;
    else
      bandLimit[id] = nullBands;


  }


  
  command error_t Exposure.read[uint8_t id]()
  {
    return call GetSensorValue.read[id]();
  }


 event void GetSensorValue.readDone[uint8_t id](error_t result, float data) {
   uint8_t x;
   uint8_t band;
   float total=0;
   if (result == SUCCESS) {

     //decay all bands
     for ( x = 0; x < num_bands[id]; x++ ) {
       bandCount[id][x] *= gamma[x];
     }
      
     //find band and increase band count and total samples
     band=findBand(data, bandLimit[id], id);
     bandCount[id][band]++;

     //calc percentages
     for ( x = 0; x < num_bands[id]; x++ ) {
       total += bandCount[id][x];
     }

     for ( x = 0; x < num_bands[id]; x++ ) {
       bandPct[id][x] = (bandCount[id][x]/total)*100.0;
     }

     //check against previous pct and decided on SUCESS or not by threshold
     signal Exposure.readDone[id](SUCCESS, bandPct[id]);
   }
   else 
     signal Exposure.readDone[id](FAIL, NULL);
 }

 /* DEFAULTS */
 default event void Exposure.readDone[uint8_t id](error_t result, float* data) {}
 default command error_t GetSensorValue.read[uint8_t id](){ return FAIL;}

}

