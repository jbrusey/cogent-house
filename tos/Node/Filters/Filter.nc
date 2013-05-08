/* -*- c -*- */

#include "Filter.h"

interface Filter
{
  /**
   * perform one filter step
   * @param t current time in milliseconds
   * @param z current sensor value
   * @param xnew returned with estimated value and rate of change
   */
  command void filter(float z, uint32_t current, FilterState *xnew);

  command void init(float a, float b); 
}

