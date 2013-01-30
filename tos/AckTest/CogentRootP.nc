// -*- c -*-
#include "AM.h"
#include "Serial.h"
#include "limits.h"

module CogentRootP{
  uses
  {
      interface Boot;
      interface SplitControl as SerialControl;
      interface SplitControl as RadioControl;

      //ack interfaces
      interface Timer<TMilli> as RandomTimer;
      interface AMSend as AckForwarder;
      interface Crc as CRCCalc ;
      interface Random;
      interface Queue<AckMsg *> as AckQueue;
      interface Pool<message_t> as AckPool;
      interface Receive as UartAckReceive;
      interface Leds;
    }
}

implementation
{
  message_t fwdMsg;
  bool fwdBusy;

  event void Boot.booted()
  {
    call SerialControl.start();
    call RadioControl.start();
  }

  event void RadioControl.startDone(error_t error) {
    if (error == FAIL)
      call RadioControl.start();
  }
	
  event void RadioControl.stopDone(error_t error) { }


  //DEAL WITH STATE
  message_t uartmsg;
  bool fwdAck=FALSE;

  event void RandomTimer.fired(){}

  task void transmit() {
    message_t dataMsg;
    AckMsg *ackData;
    AckMsg* aMsg;
    CRCStruct crs;
    uint16_t crc;
    
#ifdef BLINKY 
    call Leds.led1Toggle();
#endif
    
    if (!call AckQueue.empty() && !fwdAck) {
      aMsg = call AckQueue.dequeue();
      ackData = call AckForwarder.getPayload(&dataMsg,  sizeof(AckMsg));
      if (ackData != NULL) { 
	
	//calculate crc
	crs.node_id = aMsg->node_id;
	crs.seq = aMsg->seq;
	crc = call CRCCalc.crc16(&crs, sizeof crs);
        ackData->node_id = crs.node_id;
        ackData->seq = crs.seq;
        ackData->crc = crc;
	

	if (call AckForwarder.send(AM_BROADCAST_ADDR, &dataMsg,  sizeof(AckMsg)) == SUCCESS) {
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
	  //call Leds.led0Toggle();
#endif
    call AckPool.put(msg);
    if (! call AckQueue.empty())
      post transmit();
  }

  event message_t *UartAckReceive.receive(message_t* msg, void* payload, uint8_t len){
    AckMsg* aMsg;
#ifdef BLINKY 
    call Leds.led0Toggle();
#endif
    if (!call AckPool.empty() && call AckQueue.size() < call AckQueue.maxSize()) { 
      message_t *tmp = call AckPool.get();
      aMsg = (AckMsg*)payload;
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


}
