// -*- c -*-
module DemoBatteryM
{
  provides {
    interface Read<float>;
  }
}
implementation
{
  float battery = 3.;

  command error_t Read.read(){
    battery = battery - 0.1;
    signal Read.readDone(SUCCESS, battery);
    return SUCCESS;
  }
}
