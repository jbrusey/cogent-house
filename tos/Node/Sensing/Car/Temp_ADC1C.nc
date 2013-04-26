generic configuration Temp_ADC1C() {
  provides interface Read<uint16_t>;
  provides interface ReadStream<uint16_t>;
}
implementation {
  components new AdcReadClientC();
  Read = AdcReadClientC;

  components new AdcReadStreamClientC();
  ReadStream = AdcReadStreamClientC;

  components Temp_ADC1P;
  AdcReadClientC.AdcConfigure -> Temp_ADC1P;
  AdcReadStreamClientC.AdcConfigure -> Temp_ADC1P;
}
