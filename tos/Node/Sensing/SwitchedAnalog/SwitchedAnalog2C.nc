/* -*- c -*- */
/*************************************************************
 * SwitchedAnalog2C - module
 * 
 * Generic ADC interface that is switched on and off with 
 * a specified warm up time. 
 * 
 * J. Brusey, 27/7/2015
 *************************************************************/
generic configuration SwitchedAnalog2C(uint8_t channel, uint16_t warm_up_millis) {
  provides interface Read<float> as ReadFloat;

}
implementation {

  components new AnalogC(channel) as MyAnalog;
  components new SwitchedAnalogP(warm_up_millis);
  components SwitchGio2C;
  components new TimerMilliC() as WarmUpTimer;
  

  ReadFloat = SwitchedAnalogP.ReadFloat;
  
  SwitchedAnalogP.ReadDeviceFloat -> MyAnalog.ReadFloat;
  SwitchedAnalogP.SwitchControl -> SwitchGio2C.SwitchControl;
  SwitchedAnalogP.WarmUpTimer -> WarmUpTimer;
     
}

