/* -*- c -*- */

interface Exposure<val_t> {
  /**
   * Initialise exposure reader
   */
  command void init(uint8_t num_bands, uint8_t raw_sensor, float gamma_val); 
   
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


