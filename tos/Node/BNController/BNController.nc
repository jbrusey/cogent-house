/* -*- c -*- */

interface BNController<val_t> {
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
  
  
  /**
  * perform one filter step
  */
  command void transmissionDone();

  /**
   * Defines if an event has been triggered (pack packet and return in here?)
   */
  command bool hasEvent();
}

