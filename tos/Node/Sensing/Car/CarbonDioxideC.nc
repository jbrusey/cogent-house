generic configuration CarbonDioxideC() {
  provides interface Read<uint16_t>;
  provides interface ReadStream<uint16_t>;
}
implementation {
  components new AdcReadClientC();
  Read = AdcReadClientC;

  components new AdcReadStreamClientC();
  ReadStream = AdcReadStreamClientC;

  components CarbonDioxideP;
  AdcReadClientC.AdcConfigure -> CarbonDioxideP;
  AdcReadStreamClientC.AdcConfigure -> CarbonDioxideP;
}
