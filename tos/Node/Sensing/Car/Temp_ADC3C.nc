generic configuration Temp_ADC3C() {
  provides interface Read<uint16_t>;
  provides interface ReadStream<uint16_t>;
}
implementation {
  components new AdcReadClientC();
  Read = AdcReadClientC;

  components new AdcReadStreamClientC();
  ReadStream = AdcReadStreamClientC;

  components Temp_ADC3P;
  AdcReadClientC.AdcConfigure -> Temp_ADC3P;
  AdcReadStreamClientC.AdcConfigure -> Temp_ADC3P;
}
