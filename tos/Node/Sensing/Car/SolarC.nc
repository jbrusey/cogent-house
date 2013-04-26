generic configuration SolarC() {
  provides interface Read<uint16_t>;
  provides interface ReadStream<uint16_t>;
}
implementation {
  components new AdcReadClientC();
  Read = AdcReadClientC;

  components new AdcReadStreamClientC();
  ReadStream = AdcReadStreamClientC;

  components SolarP;
  AdcReadClientC.AdcConfigure -> SolarP;
  AdcReadStreamClientC.AdcConfigure -> SolarP;
}
