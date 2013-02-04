// -*- c -*- 
generic module DEWMAC(float x_init, float dx_init, bool init_set, float a, float b) @safe()
{
  provides interface Filter;
  provides interface Predict;
}
implementation
{
  float alpha=a;
  float beta=b;
  bool set = init_set;
  uint32_t prev_time=0;
  vec2 xhat = {x_init, dx_init};
  
  
  uint32_t subtract_time(uint32_t new_time, uint32_t old_time)
  {
    if (new_time < old_time) // deal with overflow
      return ((UINT32_MAX - old_time) + new_time + 1);
    else
      return (new_time - old_time);
  }
	
  command void Filter.filter(float z, uint32_t t, vec2 v)
  {
    float y;
    float yd;
    
    if (set==FALSE) {
        xhat[0]=z;
        xhat[1]=0;
        set=TRUE;
    }
    else
    {
        y = xhat[1] + alpha * (z - xhat[0] - xhat[1]);
        yd = beta * (y - xhat[1]);

        xhat[0] = xhat[0] + y;
        xhat[1] = (xhat[1] + yd);
    }
    mat22_copy_v(xhat, v);
  }

  /**
   * Get prediction of state based on a past state and current time.
   * @param fs "ONE FilterState *" state to use as basis for prediction
   * @param t time to predict for (usually the current time or the sense time)
   */
  command float Predict.predictState(FilterState *fs, uint32_t t)
  {
    float deltaT;
    //Find how many sensing periods have passed
    deltaT = ((float) subtract_time(t, fs->time)) / DEF_SENSE_PERIOD; 
    return fs->x + (fs->dx * deltaT);
  }		
 
}

