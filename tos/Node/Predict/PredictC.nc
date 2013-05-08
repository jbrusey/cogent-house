// -*- c -*- 
#include <stdint.h>
/*
* Module to forward predict based on a Filter state
*
*/
module PredictC
{
  provides interface Predict;
}
implementation
{
  //Subtract time method to find time between now and the last reading deals with the overflow issue
  uint32_t subtract_time(uint32_t new_time, uint32_t old_time)
  {
    if (new_time < old_time) // deal with overflow
      return ((UINT32_MAX - old_time) + new_time + 1);
    else
      return (new_time - old_time);
  }
	
  /**
   * Get prediction of state based on a past state and current time.
   * @param fs "ONE FilterState *" state to use as basis for prediction
   * @param t time to predict for (usually the current time or the sense time)
   */
  command float Predict.predictState(FilterState *fs, uint32_t t)
  {
    //Find how many sensing periods have passed
    return fs->x + fs->dx * subtract_time(t, fs->time) / 1024.f;
  }		
}

