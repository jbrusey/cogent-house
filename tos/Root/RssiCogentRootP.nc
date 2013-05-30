#include "../Packets.h"  

module RssiCogentRootP {
  uses interface Intercept as RssiMsgIntercept;
  uses interface CC2420Packet;

} implementation {

  uint16_t getRssi(message_t *msg);
  uint16_t RSSI_OFFSET = 45;
  
  event bool RssiMsgIntercept.forward(message_t *msg,
				      void *payload,
				      uint8_t len) {
    StateMsg *state = (StateMsg*) payload;
    state->rssi = getRssi(msg);
    
    return TRUE;
  }

  uint16_t getRssi(message_t *msg){
    return (uint16_t) (call CC2420Packet.getRssi(msg) - RSSI_OFFSET);
  }

}
