// -*- c -*-
#include "Sensor.h"

configuration LeafTestC {}

implementation {

  //define components that will be used
  components LeafTestP as App, MainC, LedsC;
  components ActiveMessageC;
  components new AMSenderC(AM_RADIO_SENSE_MSG);
  components new TimerMilliC();
  components HilTimerMilliC;

  //Wire componants to app
  App.Boot -> MainC;
  App.AMSend -> AMSenderC;
  App.RadioControl -> ActiveMessageC;
  App.MilliTimer -> TimerMilliC;
  App.Packet -> AMSenderC;
  App.LocalTime -> HilTimerMilliC;
  App.Leds -> LedsC;

  //Leaf node reciever
  components new AMReceiverC(AM_LEAF_ACK_MSG);
  App.Receive -> AMReceiverC;
}
