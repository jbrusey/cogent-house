/* -*- c -*- */
/*************************************************************
 * SwitchedAnalog3C - module
 * 
 * Generic ADC interface that is switched on and off with 
 * a specified warm up time. 
 * 
 * J. Brusey, 27/7/2015
 *************************************************************/
generic configuration SwitchedAnalog3C(uint8_t channel, uint16_t warm_up_millis) {
  provides interface Read<float> as ReadFloat;

}
implementation {

  components new AnalogC(channel) as MyAnalog;
  components new SwitchedAnalogP(warm_up_millis) as MySwitchedAnalog;
  components SwitchGio3C;

  ReadFloat = MySwitchedAnalog.ReadFloat;
  
  MySwitchedAnalog.ReadDeviceFloat -> MyAnalog.ReadFloat;
  MySwitchedAnalog.SwitchControl -> SwitchGio3C.SwitchControl;
     
}

