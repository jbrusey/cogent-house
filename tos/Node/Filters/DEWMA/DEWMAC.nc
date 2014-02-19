// -*- c -*- 
#include "Filter.h"
#include "subtracttime.h"

module DEWMAC @safe()
{
  provides interface Filter[uint8_t id];
}
implementation
{
  float alpha[RS_SIZE];
  float beta[RS_SIZE];
  uint32_t count[RS_SIZE];
  FilterState xhat[RS_SIZE];



  /* run filter step
   * 
   * z - sensed value
   * current - sensed time
   * v - vector to copy results back to
   */
  command void Filter.filter[uint8_t id](float z, uint32_t current, FilterState *xnew)
  {
    uint32_t delta_t;
    xnew->time = current;
    xnew->z = z; /* TODO remove z from filterstate */

    if (count[id] == 0) {
      xnew->x = z;
      xnew->dx = 0;
      count[id]++;
    }
    else{
      delta_t = subtract_time(current, xhat[id].time);
      xnew->x = alpha[id] * z + (1-alpha[id]) * (xhat[id].x + (xhat[id].dx * delta_t / 1024.f));
      if (delta_t == 0) {
	xnew->dx = xhat[id].dx;
      }
      else{
	/* if (count[id] == 1) {  */
	/*   xnew->dx = (z - xhat[id].x) / delta_t * 1024.f; */
	/*   count[id]++; */
	/* } */
	/* else { */
	xnew->dx = beta[id] * (xnew->x - xhat[id].x) / delta_t * 1024.f +
	  (1 - beta[id]) * xhat[id].dx;
	/* } */
      }
    }
    xhat[id] = *xnew;
  }


/* initialises the parameters for the filter
 * 
 * x_init - intiial x value
 * dx_init - initial dx value
 * init_set - if to set the initial values or not
 * a - smoothing parameter in range (0,1)
 * b - second order smoothing parameter in range (0,1)
 */
 command void Filter.init[uint8_t id](float a, float b){
   count[id] = 0;
   alpha[id] = a;
   beta[id] = b;
   xhat[id].x = 0.;
   xhat[id].dx = 0.;
   xhat[id].time = 0;
 }

}

