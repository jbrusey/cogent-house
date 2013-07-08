/* -*- c -*- */

interface SIPController<val_t> {
  /**
   * initialise state
   */
  command void init(float threshold, bool sensorMask, float a, float b);

 
  /**
   * Initiates a read of the value.
   * 
   * @return SUCCESS if a readDone() event will eventually come back.
   */
  command error_t read();

  /**
   * Signals the completion of the read().
   *
   * @param result SUCCESS if the read() was successful
   * @param val the value that has been read
   */
  event void readDone( error_t result, val_t val ); 
}

