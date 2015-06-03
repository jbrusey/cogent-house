/* -*- c -*- */
interface BootMessage {
  /**
   * send - send a boot message and wait for send completion or
   * timeout.
   * 
   * @return SUCCESS if a sendDone() event will eventually come back.
   */
  command error_t send();

  /**
   * Signals the completion of the send() or timeout.
   *
   * @param result SUCCESS if the send() was successful
   */
  event void sendDone( error_t result );
}
