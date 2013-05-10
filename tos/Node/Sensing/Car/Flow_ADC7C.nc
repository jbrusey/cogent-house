generic configuration Flow_ADC7C() {
  provides interface Read<uint16_t>;
  provides interface ReadStream<uint16_t>;
}
implementation {
  components new AdcReadClientC();
  Read = AdcReadClientC;

  components new AdcReadStreamClientC();
  ReadStream = AdcReadStreamClientC;

  components Flow_ADC7P;
  AdcReadClientC.AdcConfigure -> Flow_ADC7P;
  AdcReadStreamClientC.AdcConfigure -> Flow_ADC7P;
}
