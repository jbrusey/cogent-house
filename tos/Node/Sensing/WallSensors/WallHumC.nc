generic configuration WallHumC() {
  provides interface Read<uint16_t>;
  provides interface ReadStream<uint16_t>;
}
implementation {
  components new AdcReadClientC();
  Read = AdcReadClientC;

  components new AdcReadStreamClientC();
  ReadStream = AdcReadStreamClientC;

  components WallHumP;
  AdcReadClientC.AdcConfigure -> WallHumP;
  AdcReadStreamClientC.AdcConfigure -> WallHumP;
}
