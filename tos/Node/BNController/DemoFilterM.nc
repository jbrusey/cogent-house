// -*- c -*-
module DemoFilterM
{
  provides {
    interface Read<float*>;
  }
}
implementation
{
  float currentState[5];

  command error_t Read.read(){
    currentState[2]++;
    signal Read.readDone(SUCCESS, currentState);
    return SUCCESS;
  }
}
