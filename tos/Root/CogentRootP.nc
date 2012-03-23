// -*- c -*-
#include "AM.h"
#include "Serial.h"

module CogentRootP @safe() {
  uses {
    interface Boot;
    interface SplitControl as SerialControl;
    interface SplitControl as RadioControl;
    
    interface AMSend as UartSend[am_id_t id];
    interface Receive as UartAckReceive;
    interface Packet as UartPacket;
    interface AMPacket as UartAMPacket;
    
    interface AMSend as RadioSend;
    interface Receive as RadioReceive;
    interface Packet as RadioPacket;
    interface AMPacket as RadioAMPacket;
    
    // queuing
    interface Queue<message_t *>;
    interface Pool<message_t>;
    
    interface Timer<TMilli> as BlinkTimer;
    interface Leds;
  }
}

implementation
{
  message_t fwdMsg;
  bool fwdBusy;
  uint8_t lastLen;

  event void Boot.booted()
  {
    call SerialControl.start();
    call RadioControl.start();
    //call BlinkTimer.startOneShot(512L);
  }

  event void RadioControl.startDone(error_t error) {
    if (error == FAIL)
      call RadioControl.start();
  }
	
  event void RadioControl.stopDone(error_t error) { }


  //DEAL WITH STATE
  message_t uartmsg;

  task void serialForwardTask() { 
    if (!call Queue.empty() && !fwdBusy) {
      message_t* msg = call Queue.dequeue();
      uint8_t len = call RadioPacket.payloadLength(msg);
      void *radio_payload = call RadioPacket.getPayload(msg, len);
      am_id_t id = call RadioAMPacket.type(msg);
      am_addr_t src = call RadioAMPacket.source(msg);

      if (radio_payload != NULL) { 
	void *uart_payload;
	memcpy(&uartmsg, radio_payload, len);

#ifdef BLINKY 
	if (((StateMsg *) radio_payload)->special != 0xc7)
	  call Leds.led1On();
#endif
	call UartPacket.clear(msg);
	call UartAMPacket.setSource(msg, src);
	uart_payload = call UartPacket.getPayload(msg, len);
	if (uart_payload != NULL) { 
	  memcpy(uart_payload, &uartmsg, len);
#ifdef BLINKY 
	  if (((StateMsg *) uart_payload)->special != 0xc7)
	    call Leds.led2On();
#endif
      
	  if (call UartSend.send[id](AM_BROADCAST_ADDR, msg, len) == SUCCESS) { 
	    fwdBusy = TRUE;
	  }
	  else { 
#ifdef BLINKY
	    call Leds.led0On();
#endif
	  }
	}
      }
    }
  }
  

  event message_t *RadioReceive.receive(message_t* msg, 
						    void* payload, 
						    uint8_t len)
  {
#ifdef BLINKY
    call Leds.led1Toggle();
#endif
    if (!call Pool.empty() && call Queue.size() < call Queue.maxSize()) { 
      message_t *tmp = call Pool.get();
      call Queue.enqueue(msg);
      if (!fwdBusy) {
	post serialForwardTask();
      }
      return tmp;
    }
    return msg;
  }

  event void UartSend.sendDone[am_id_t id](message_t *msg, error_t error) {
    fwdBusy = FALSE;
    call Pool.put(msg);
    if (! call Queue.empty())
      post serialForwardTask();
  }

  /** send ack */
  event message_t* UartAckReceive.receive(message_t* msg, void* payload, uint8_t len)
  {
    am_addr_t addr = call UartAMPacket.destination(msg);
    call Leds.led0Toggle();

    call RadioSend.send(addr, msg, len);
    return msg;
  }


  event void RadioSend.sendDone(message_t* msg, error_t error) {
    call Leds.led2Toggle();
  }

  event void SerialControl.startDone(error_t error) {
    fwdBusy = FALSE;
    if (error == FAIL)
      call SerialControl.start();
  }
  event void SerialControl.stopDone(error_t error) { }

  uint8_t blink_state = 0;

  uint8_t gray[] = { 0, 1, 3, 2 };

  event void BlinkTimer.fired() { 
    if (blink_state >= 60) { /* 30 seconds */
      call Leds.set(0);
    }
    else { 
      blink_state++;
      call BlinkTimer.startOneShot(512L);
      call Leds.set(gray[blink_state % (sizeof gray / sizeof gray[0])]);
    }
  }
    


}
