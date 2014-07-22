generic configuration BlackBulbC() {
  provides interface Read<uint16_t>;
  provides interface ReadStream<uint16_t>;
}
implementation {
  components new AdcReadClientC();
  Read = AdcReadClientC;

  components new AdcReadStreamClientC();
  ReadStream = AdcReadStreamClientC;

  components BlackBulbP;
  AdcReadClientC.AdcConfigure -> BlackBulbP;
  AdcReadStreamClientC.AdcConfigure -> BlackBulbP;
}

