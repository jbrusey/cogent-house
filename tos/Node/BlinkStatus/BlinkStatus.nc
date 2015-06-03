/* -*- c -*- */
interface BlinkStatus {
  /**
   * start - start a blink sequence
   * 
   */
  command void start();

  /**
   * setStatus - set a status flag of SUCCESS or FAIL
   *
   */
  command void setStatus( error_t flag );

  /**
   * getStatus - get current status flag
   *
   */
  command error_t getStatus( );
}
