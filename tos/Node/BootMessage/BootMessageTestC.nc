// -*- c -*-
enum { 
  AM_BOOT_MSG = 8
};

configuration BootMessageTestC
{}

implementation
{
  components MainC, BootMessageTestP;

  components PrintfC, SerialStartC;

  components LedsC;
  components BootMessageC;

  BootMessageTestP.Boot -> MainC.Boot;

  // Instantiate and wire our collection service
  components CollectionC, ActiveMessageC;
  components new CollectionSenderC(AM_BOOT_MSG) as BootSender;

  BootMessageTestP.RadioControl -> ActiveMessageC;
  BootMessageTestP.CollectionControl -> CollectionC;
  BootMessageC.BootSender-> BootSender;

  BootMessageTestP.Leds -> LedsC;
  BootMessageTestP.BootMessage -> BootMessageC;
}
