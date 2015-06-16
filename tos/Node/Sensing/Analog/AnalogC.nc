/* -*- c -*- */
/*************************************************************
 * AnalogC - module
 * 
 * generic ADC module that uses a 2.5 ref voltage. The ADC 12 bit
 * value is converted into a floating point voltage before being
 * returned.
 *
 * J. Brusey, 16/5/2015
 *************************************************************/
generic configuration AnalogC(uint8_t channel) {
  provides interface Read<float> as ReadFloat;

}
implementation {
  components new AdcReadClientC();

  components new AnalogP(channel) as MyAnalog;
  AdcReadClientC.AdcConfigure -> MyAnalog;
  MyAnalog.ReadAdc -> AdcReadClientC;
  ReadFloat = MyAnalog.ReadFloat;
}

