// -*- c -*-
module DemoFilterM
{
  provides 
    {
      interface Read<FilterState*>;
    }
}
implementation
{
  uint32_t time;
  float i=0;
  
  command error_t Read.read()
  {
    FilterState currentState;
    currentState.z = i;
    currentState.time = i;
    currentState.x = i;
    currentState.dx = 0;
    signal Read.readDone(SUCCESS, &currentState);	
    i=i+1;
  }
}
