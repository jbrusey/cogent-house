// -*- c -*-


module CogentRootP @safe() {
  uses {
      interface Boot;
      interface SplitControl as SerialControl;
      interface SplitControl as RadioControl;

      interface StdControl as CollectionControl;
      interface RootControl;

      //receive interfaces
      interface Receive as CollectionReceive[am_id_t id];
      interface Packet as RadioPacket;
      interface CollectionPacket;

      //ack interfaces
      interface AMSend as AckForwarder;
      interface Packet;
      interface Crc as CRCCalc ;
      interface Queue<AckMsg_t *> as AckQueue;
      interface Pool<message_t> as AckPool;

      //data forwarding interfaces
      interface AMSend as UartSend[am_id_t id];
      interface Packet as UartPacket;
      interface AMPacket as UartAMPacket;
      interface Receive as UartAckReceive;

      // queuing
      interface Queue<message_t *> as DataQueue;
      interface Pool<message_t> as DataPool;

      interface Timer<TMilli> as BlinkTimer;
      interface Leds;
    }
}

implementation
{
  message_t fwdMsg;
  bool fwdBusy;
  bool fwdAck = FALSE;
  message_t dataMsg;
  message_t uartmsg;

  event void Boot.booted()
  {
    call SerialControl.start();
    call RadioControl.start();
    call BlinkTimer.startOneShot(512L);
  }

  event void RadioControl.startDone(error_t error) {
    if (error == FAIL)
      call RadioControl.start();
    else {
      call CollectionControl.start();
      call RootControl.setRoot();
    }
  }
	
  event void RadioControl.stopDone(error_t error) { }


  //DEAL WITH STATE
  task void serialForwardTask() { 
    if (!call DataQueue.empty() && !fwdBusy) {
      message_t* msg = call DataQueue.dequeue();
      uint8_t len = call RadioPacket.payloadLength(msg);
      void *radio_payload = call RadioPacket.getPayload(msg, len);
      collection_id_t id = call CollectionPacket.getType(msg);
      am_addr_t src = call CollectionPacket.getOrigin(msg);

      if (radio_payload != NULL) { 
	void *uart_payload;
	memcpy(&uartmsg, radio_payload, len);

	call UartPacket.clear(msg);
	call UartAMPacket.setSource(msg, src);
	uart_payload = call UartPacket.getPayload(msg, len);
	if (uart_payload != NULL) { 
	  memcpy(uart_payload, &uartmsg, len);
      
	  if (call UartSend.send[id](AM_BROADCAST_ADDR, msg, len) == SUCCESS) { 
	    fwdBusy = TRUE;
	  }
	  else { 
#ifdef BLINKY
	    //	    call Leds.led0Toggle();
#endif
	  }
	}
      }
    }
  }
  

  event message_t *CollectionReceive.receive[collection_id_t id](message_t* msg, 
						    void* payload, 
						    uint8_t len)
  {
#ifdef BLINKY
    //    call Leds.led2Toggle();
#endif
    if (!call DataPool.empty() && call DataQueue.size() < call DataQueue.maxSize()) { 
      message_t *tmp = call DataPool.get();
      call DataQueue.enqueue(msg);
      if (!fwdBusy) {
	post serialForwardTask();
      }
      return tmp;
    }
    return msg;
  }

  event void UartSend.sendDone[am_id_t id](message_t *msg, error_t error) {
    fwdBusy = FALSE;
    call DataPool.put(msg);
    if (! call DataQueue.empty())
      post serialForwardTask();
  }


  task void transmit() {
    AckMsg_t *ackData;
    AckMsg_t* aMsg;
    CRCStruct crs;
    uint16_t crc;
    
#ifdef BLINKY 
    call Leds.led1Toggle();
#endif
    
    if (!call AckQueue.empty() && !fwdAck) {
      aMsg = call AckQueue.dequeue();
      ackData = (AckMsg_t *) call Packet.getPayload(&dataMsg,  sizeof (AckMsg_t));
      if (ackData != NULL) { 
	
	//calculate crc
	crs.node_id = aMsg->node_id;
	crs.seq = aMsg->seq;
	crc = call CRCCalc.crc16(&crs, sizeof crs);
        ackData->node_id = crs.node_id;
        ackData->seq = crs.seq;
        ackData->crc = crc;
	if (call AckForwarder.send(AM_BROADCAST_ADDR, &dataMsg,  sizeof (AckMsg_t)) == SUCCESS) {
	  fwdAck = TRUE;	
#ifdef BLINKY
	  call Leds.led2On();
#endif
	}	  
      }
    }
  }

  event void AckForwarder.sendDone(message_t *msg, error_t ok) {
    fwdAck = FALSE;
#ifdef BLINKY
    call Leds.led2Off();
#endif
	
#ifdef BLINKY 
    call Leds.led0Toggle();
#endif
    call AckPool.put(msg);
    if (! call AckQueue.empty())
      post transmit();
  }

  event message_t *UartAckReceive.receive(message_t* msg, void* payload, uint8_t len){
    AckMsg_t* aMsg;
#ifdef BLINKY
    call Leds.led0Toggle();
#endif
    if (!call AckPool.empty() && call AckQueue.size() < call AckQueue.maxSize()) {
      message_t *tmp = call AckPool.get();
      aMsg = (AckMsg_t*)payload;
      call AckQueue.enqueue(aMsg);
      
      if (!fwdAck)
	post transmit();
      
      return tmp;
    }
    return msg;
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
