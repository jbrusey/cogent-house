// -*- c -*- 
module DEWMAC @safe()
{
  provides interface Filter[uint8_t id];
}
implementation
{
  float alpha[RS_SIZE];
  float beta[RS_SIZE];
  uint32_t count[RS_SIZE];
  uint32_t old_time[RS_SIZE];
  bool set[RS_SIZE];
  vec2 xhat[RS_SIZE]; 


  //Subtract time method to find time between now and the last reading deals with the overflow issue
  uint32_t subtract_time(uint32_t current_time, uint32_t prev_time)
  {
    if (current_time < prev_time) // deal with overflow
      return ((UINT32_MAX - prev_time) + current_time + 1);
    else
      return (current_time - prev_time);
  }


  /* run filter step
   * 
   * z - sensed value
   * current - sensed time
   * v - vector to copy results back to
   */
  command void Filter.filter[uint8_t id](float z, uint32_t current, vec2 v)
  {
    float delta_t;

    if (count[id] == 0) {
      xhat[id][0] = z;
      xhat[id][1] = 0;
      count[id]++;
    }
    else{
      delta_t = subtract_time(current, old_time[id]);
      xhat[id][0] = alpha[id] * z + (1-alpha[id]) * (xhat[id][0] + xhat[id][1]);
      if (delta_t == 0) {
	xhat[id][1] = xhat[id][1];
      }
      else{
	if (count[id] == 1) { 
	  xhat[id][1] = (z - xhat[id][0]) / delta_t;
	  count[id]++;
	}
	else {
	  xhat[id][1] = beta[id] * (xhat[id][0] - xhat[id][0]) / delta_t +
	    (1 - beta[id]) * xhat[id][1];
	}
      }
    }
    old_time[id] = current;
    mat22_copy_v(xhat[id], v);
  }


/* initialises the parameters for the filter
 * 
 * x_init - intiial x value
 * dx_init - initial dx value
 * init_set - if to set the initial values or not
 * a - smoothing parameter in range (0,1)
 * b - second order smoothing parameter in range (0,1)
 */
 command void Filter.init[uint8_t id](float x_init, float dx_init, bool init_set, float a, float b){
   count[id] = 0;
   old_time[id] = 0;
   alpha[id] = a;
   beta[id] = b;
   set[id] = init_set;
   if(init_set){
     xhat[id][0] = x_init;
     xhat[id][1] = dx_init;
   }
   else{
     xhat[id][0] = 0.;
     xhat[id][1] = 0.;
   }
 }

}

