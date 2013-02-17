/* -*- c -*- */

#include "mat22.h"

interface Filter
{
  /**
   * perform one filter step
   * @param t current time in milliseconds
   * @param z current sensor value
   * @param v returned with estimated value and rate of change
   */
  command void filter(float z, uint32_t t, float* v);
}

