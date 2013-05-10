generic configuration Solar_ADC3C() {
  provides interface Read<uint16_t>;
  provides interface ReadStream<uint16_t>;
}
implementation {
  components new AdcReadClientC();
  Read = AdcReadClientC;

  components new AdcReadStreamClientC();
  ReadStream = AdcReadStreamClientC;

  components Solar_ADC3P;
  AdcReadClientC.AdcConfigure -> Solar_ADC3P;
  AdcReadStreamClientC.AdcConfigure -> Solar_ADC3P;
}
