// -*- c -*- 

#include "subtracttime.h"

module PassThroughC @safe()
{
  provides interface Filter[uint8_t id];
}
implementation
{
  FilterState xhat[RS_SIZE];

  command void Filter.filter[uint8_t id](float z, uint32_t t, FilterState * v)
  {   
    v->x = z;
    v->dx = (v->x - xhat[id].x) /
      subtract_time(t, xhat[id].time) * 1024.f;
    v->z = z;
    v->time = t;
    xhat[id] = *v;
  } 

  command void Filter.init[uint8_t id](float a, float b){}
}


