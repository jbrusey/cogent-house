generic configuration Flow_ADC3C() {
  provides interface Read<uint16_t>;
  provides interface ReadStream<uint16_t>;
}
implementation {
  components new AdcReadClientC();
  Read = AdcReadClientC;

  components new AdcReadStreamClientC();
  ReadStream = AdcReadStreamClientC;

  components Flow_ADC3P;
  AdcReadClientC.AdcConfigure -> Flow_ADC3P;
  AdcReadStreamClientC.AdcConfigure -> Flow_ADC3P;
}
