#ifndef _SUBTRACTTIME_H
#define _SUBTRACTTIME_H
  //Subtract time method to find time between now and the last reading deals with the overflow issue
  uint32_t subtract_time(uint32_t current_time, uint32_t prev_time)
  {
    if (current_time < prev_time) // deal with overflow
      return ((UINT32_MAX - prev_time) + current_time + 1);
    else
      return (current_time - prev_time);
  }

#endif
