generic configuration Temp_ADC2C() {
  provides interface Read<uint16_t>;
  provides interface ReadStream<uint16_t>;
}
implementation {
  components new AdcReadClientC();
  Read = AdcReadClientC;

  components new AdcReadStreamClientC();
  ReadStream = AdcReadStreamClientC;

  components Temp_ADC2P;
  AdcReadClientC.AdcConfigure -> Temp_ADC2P;
  AdcReadStreamClientC.AdcConfigure -> Temp_ADC2P;
}
