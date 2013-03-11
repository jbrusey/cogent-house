// -*- c -*- 
module DEWMAC @safe()
{
  provides interface Filter[uint8_t id];
}
implementation
{
  float alpha[RS_SIZE];
  float beta[RS_SIZE];
  bool set[RS_SIZE];
  vec2 xhat[RS_SIZE]; 

  
  command void Filter.filter[uint8_t id](float z, uint32_t t, vec2 v)
  {
    float y;
    float yd;
    
    if (set[id]==FALSE) {
      xhat[id][0] = z;
      xhat[id][1] = 0;
      set[id] = TRUE;
    }
    else
    {
      y = xhat[id][1] + alpha[id] * (z - xhat[id][0] - xhat[id][1]);
      yd = beta[id] * (y - xhat[id][1]);

      xhat[id][0] = xhat[id][0] + y;
      xhat[id][1] = (xhat[id][1] + yd);
    }
    mat22_copy_v(xhat[id], v);
  } 

 command void Filter.init[uint8_t id](float x_init, float dx_init, bool init_set, float a, float b){
   alpha[id] = a;
   beta[id] = b;
   set[id] = init_set;
   if(init_set){
     xhat[id][0] = x_init;
     xhat[id][1] = dx_init;
   }
   else{
     xhat[id][0] = 0.;
     xhat[id][1] = 0.;
   }
 }
}

