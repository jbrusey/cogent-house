// -*- c -*-
#include <stdint.h>
#include "Filter.h"
module DemoPredictM
{
  provides 
    {
      interface Predict;
    }
}
implementation
{

  uint32_t subtract_time(uint32_t new_time, uint32_t old_time)
  {
    if (new_time < old_time) // deal with overflow
      return ((UINT32_MAX - old_time) + new_time + 1);
    else
      return (new_time - old_time);
  }

  command float Predict.predictState(FilterState *fs, uint32_t t)
  {
    float deltaT;
    deltaT = (float) subtract_time(t, fs->time) / 1024.0;
    return fs->x + fs->dx * deltaT;
  }
  
}
