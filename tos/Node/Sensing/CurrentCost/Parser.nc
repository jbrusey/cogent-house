/* -*- c -*- */
/*************************************************************
 *
 * Parser.nc
 *
 * simplified xml parser for dealing with current cost
 *
 * @author James Brusey
 * @date 2011-05-17
 *
 * history:
 * 1. conversion to C
 * 2. conversion to nesc, may 2011
 *
 *************************************************************/

interface Parser {
  /**
   * parse next message
   * 
   * @return SUCCESS if all ok and FAIL if an error occurred.
   */
  command error_t parse();

  /** 
   * get the last error message if any
   *
   * @return pointer to error string buffer (owned by Parser) 
   */
  command char *lastError();

  /** 
   * Called when a value has been found in message.
   *
   * @param path pathname of value such as "/msg/tmpr"
   * @value string value found
   */
  event void onValue(char *path, char *value);
}
