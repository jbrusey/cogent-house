// -*- c -*- 
generic module ExposureC(uint8_t num_bands, uint raw_sensor, float gamma) @safe()
{
  provides interface Read<float*>;
  uses interface Read<float> as GetValue;
}
implementation
{
  float bandCount[num_bands];
  float bandPct[num_bands];
  float *bandLimit;
  bool first=TRUE;

  void getLimits(){
    if (raw_sensor == RS_TEMPERATURE)
      bandLimit=tBands;
    else if (raw_sensor == RS_HUMIDITY)
      bandLimit=hBands;
    else if (raw_sensor == RS_CO2)
      bandLimit=cBands;
    else if (raw_sensor == RS_VOC)
      bandLimit=vBands;
    else if (raw_sensor == RS_AQ)
      bandLimit=aBands;
    else
      bandLimit=nullBands;
  } 
  
  //find in which band a value falls.
  uint8_t findBand(float k, float* bands)
  {
    uint8_t x;

    for ( x = 0; x < (num_bands); x++ ) {
      if (k <= bandLimit[x]){
	return x;
      }
    }
    return num_bands-1;
  }
  
  command error_t Read.read()
  {
    return call GetValue.read();
  }


 event void GetValue.readDone(error_t result, float data) {
   uint8_t x;
   uint8_t band;
   float total=0;
   if (result == SUCCESS) {
      if (first){
       getLimits();
       first=FALSE;
     }

     //decay all bands
     for ( x = 0; x < num_bands; x++ ) {
       total *= gamma;
       bandCount[x] *= gamma;
     }
      
     //find band and increase band count and total samples
     band=findBand(data, bandLimit);
     bandCount[band]++;

     //calc percentages
     for ( x = 0; x < num_bands; x++ ) {
       total += bandCount[x];
     }

     for ( x = 0; x < num_bands; x++ ) {
       bandPct[x] = (bandCount[x]/total)*100.0;
     }

     //check against previous pct and decided on SUCESS or not by threshold

     signal Read.readDone(result, bandPct);
   }
   else 
     signal Read.readDone(result, NULL);
 }

}

