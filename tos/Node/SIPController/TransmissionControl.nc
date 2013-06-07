/* -*- c -*- */

interface TransmissionControl
{ 

  /**
   * perform one filter step
   */
  command void transmissionDone();

  /**
   * Defines if an event has been triggered (pack packet and return in here?)
   */
  command bool hasEvent();
}

