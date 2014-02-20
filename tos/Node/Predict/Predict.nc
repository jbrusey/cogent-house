/* -*- c -*- */

#include "Filter.h"

interface Predict{
  /**
   * Get prediction of state based on a past state and current time.
   * @param fs "ONE FilterState *" state to use as basis for prediction
   * @param t time to predict for (usually the current time or the sense time)
   */
  command float predictState(FilterState *fs, uint32_t t);
}
