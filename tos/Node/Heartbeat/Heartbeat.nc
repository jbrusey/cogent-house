/* -*- c -*- */

interface Heartbeat
{ 
  /**
   * initialise state
   */
  command void init();
  
 /**
   * Check if heartbeat has been triggered
   */
  command bool triggered();

  /**
   * Teset to inital values
   */
  command void reset();
}

