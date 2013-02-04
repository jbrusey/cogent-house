/* -*- c -*- */

interface TransmissionControl
{ 
  /**
   * initialise state
   */
  command void init(float threshold);

  /**
   * perform one filter step
   */
  command void transmissionDone();
}

