// -*- c -*- 
module PassThroughC @safe()
{
  provides interface Filter[uint8_t id];
}
implementation
{
  vec2 xhat[RS_SIZE];

  command void Filter.filter[uint8_t id](float z, uint32_t t, vec2 v)
  {   
    xhat[id][0] = z;
    mat22_copy_v(xhat[id], v);
  } 

  command void Filter.init[uint8_t id](float x_init, float dx_init, bool init_set, float a, float b){}
}


