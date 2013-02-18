#include "../Packets.h"
#include "message.h"

configuration RssiCogentRootC {} 
implementation {
  components CogentRootC;
  components RssiCogentRootP as App;

  components CC2420ActiveMessageC;
  App -> CC2420ActiveMessageC.CC2420Packet;
  App-> CogentRootC.RadioIntercept[AM_STATEMSG];
}
