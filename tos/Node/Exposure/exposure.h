#ifndef EXPOSURE_H
#define EXPOSURE_H


float tBands[4] = {16., 18., 22., 27.};
float hBands[3] = {45., 65., 85.};
float cBands[3] = {600., 1000., 2500.};
float vBands[1] = {1000.};
float aBands[1] = {1.5};
float nullBands[4] = {0., 0., 0., 0.};

enum{
  TEMP_BAND_LEN = sizeof tBands,
  HUM_BAND_LEN = sizeof hBands,
  CO2_BAND_LEN = sizeof cBands,
  VOC_BAND_LEN = sizeof vBands,
  AQ_BAND_LEN = sizeof aBands,
};


#endif
