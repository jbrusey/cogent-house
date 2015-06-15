// -*- c -*-

configuration SensingTestC
{}

implementation
{
  components MainC, SensingTestP;

  components PrintfC, SerialStartC;

  components LedsC;
  components SensingC;

  SensingTestP.Boot -> MainC.Boot;

  SensingTestP.Leds -> LedsC;
  SensingTestP.Sensing -> SensingC;

  SensingTestP.Configured -> SensingC;
  SensingTestP.PackState -> SensingC;
}
