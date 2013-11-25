// -*- c -*-
#include "AM.h"
#include "Serial.h"

#include "TestSerial.h"


module TestUARTP @safe() {
  uses {
      interface Boot;
      interface SplitControl as SerialControl;

      //data forwarding interfaces
      interface AMSend as UartSend[am_id_t id];
      interface Packet as UartPacket;
      interface AMPacket as UartAMPacket;
      
      // queuing
      interface Queue<message_t *>;
      interface Pool<message_t>;

      //errors
      interface StdControl as ErrorDisplayControl;
      interface ErrorDisplay;
      interface Leds;
    }
    
  provides interface Intercept as RadioIntercept[am_id_t amid];
}

implementation
{
  //message_t fwdMsg;
  bool locked = FALSE;
  message_t uartmsg;
  message_t packet;
  uint16_t counter = 0;

  event void Boot.booted()
  {
    call SerialControl.start();
  }


  task void sendIt() { 
    //send packet

    uint8_t id = 5;
    counter++;
    if (locked) {
      return;
    }
    else {
      test_serial_msg_t* rcm = (test_serial_msg_t*)call UartPacket.getPayload(&packet, sizeof(test_serial_msg_t));
      if (rcm == NULL) {return;}
      if (call UartPacket.maxPayloadLength() < sizeof(test_serial_msg_t)) {
	return;
      }
      
      if (call UartSend.send[id](AM_BROADCAST_ADDR, &packet, sizeof(test_serial_msg_t)) == SUCCESS) {
	locked = TRUE;
      }
    }

  }

 

  event void UartSend.sendDone[am_id_t id](message_t *msg, error_t error) {
    if (error == SUCCESS)
      call Leds.led1Toggle();
    if (&packet == msg){
      locked = FALSE;
      post sendIt();
    }
  }


  event void SerialControl.startDone(error_t error) {
    if (error == FAIL)
      call SerialControl.start();
    post sendIt();
  }

  event void SerialControl.stopDone(error_t error) {}



}

