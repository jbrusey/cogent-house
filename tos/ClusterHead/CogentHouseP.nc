// -*- c -*-

module CogentHouseP
{
  uses {
    //low-level stuff
    interface Timer<TMilli> as BlinkTimer;
    interface Leds;
    interface Boot;
    
    //radio
    interface SplitControl as RadioControl;
    interface AMSend as StateForwarder;
    interface AMSend as BNForwarder;
    interface AMSend as AckForwarder;
    interface Receive as AckReceiver;
    interface Receive as StateReceiver;
    interface Receive as BNReceiver;


    // queuing
    interface Queue<StateMsg*> as SMQueue;
    interface Pool<message_t> as SMPool;
    interface Queue<StateMsg*> as BNQueue;
    interface Pool<message_t> as BNPool;
    interface Queue<AckMsg*> as ACKQueue;
    interface Pool<message_t> as ACKPool;


    //Time
    interface LocalTime<TMilli>;
  }
}
implementation
{

  bool sending;
  message_t fwdMsg;
  message_t ackMsg;

  
  ////////////////////////////////////////////////////////////
	
  event void Boot.booted() {
    // initial config
#ifdef DEBUG
    printf("Booted %lu\n", call LocalTime.get());
    printfflush();
#endif

    call RadioControl.start();
    call BlinkTimer.startOneShot(512L); /* start blinking to show that we are up and running */
    sending = FALSE;
  }


  event void RadioControl.startDone(error_t ok) {
    if (ok == SUCCESS)
      {
#ifdef DEBUG
        printf("Radio On\n");
        printfflush();
#endif
      }
    else
      call RadioControl.start();
  }


  //Empty methods
  event void RadioControl.stopDone(error_t ok) { 
#ifdef BLINKY
    call Leds.led1Toggle(); 
#endif
  }


  ////////////////////////////////////////////////////////////
  // Produce a nice pattern on start-up
  //
  uint8_t blink_state = 0;

  uint8_t gray[] = { 0, 1, 3, 2, 6, 7, 5, 4 };

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

  task void SMForwardTask();
  task void BNForwardTask();
  //---------------- Deal with Acknowledgements --------------------------------

   task void AckForwardTask() { 
    AckMsg *ackData;
    AckMsg* aMsg;
    int prev_hop;
    uint16_t dest;
    if (!call ACKQueue.empty() && !sending) {
      aMsg = call ACKQueue.dequeue();
      ackData = call StateForwarder.getPayload(&fwdMsg,  sizeof(AckMsg));
      if (ackData != NULL) { 
	prev_hop=(aMsg->hops)-1;
	if (prev_hop>=0){
	  dest=aMsg->route[prev_hop];
	  ackData->hops=prev_hop;
	  ackData->seq = aMsg->seq;
	    
	  memcpy(ackData->route, aMsg->route, sizeof aMsg->route);
	    
#ifdef DEBUG
	  printf("Forward ACK %lu\n", call LocalTime.get());
	  printf("Hops %u\n", h);
	  printf("NID %u\n", TOS_NODE_ID);
	  printf("Dest %u\n", dest);
	  printfflush();
#endif
	  if (call AckForwarder.send(dest, &ackMsg,  sizeof(ackMsg))==SUCCESS){
	    sending = TRUE;
	  }
	}
      }
    }
  }


  //Receive a message repack and forward up to the next cluster head
  event message_t* AckReceiver.receive(message_t* msg,void* payload, uint8_t len) {
    AckMsg* aMsg;
    if (!call ACKPool.empty() && call ACKQueue.size() < call ACKQueue.maxSize()) { 
      message_t *tmp = call ACKPool.get();
      aMsg = (AckMsg*)payload;
      if (len == sizeof(AckMsg)){
	call ACKQueue.enqueue(aMsg);
	if (!sending) {
	  post AckForwardTask();
	}
	return tmp;
      }
    }  
    return msg; 
  }

  event void AckForwarder.sendDone(message_t *msg, error_t ok) {
    call ACKPool.put(msg);
    if (! call ACKQueue.empty())
      post AckForwardTask();
    if (! call SMQueue.empty())
      post SMForwardTask();
    if (! call BNQueue.empty())
      post BNForwardTask();
    sending = FALSE;
  }


  //---------------- Deal with State Message Forwarding---------------------

   task void SMForwardTask() { 
    StateMsg *newData;
    int i;
    int next_hop;
    StateMsg* sMsg;
    if (!call SMQueue.empty() && !sending) {
      sMsg = call SMQueue.dequeue();
      newData = call StateForwarder.getPayload(&fwdMsg,  sizeof(StateMsg));
      if (newData != NULL) { 
	next_hop=(sMsg->hops)+1;
	if (next_hop<=MAX_HOPS){
	  newData->timestamp = sMsg->timestamp;
	  newData->special = sMsg->special;
	  newData->hops = next_hop;
	  
	  //loop through and pack the route adding this node on at the end
	  for (i = 0; i < MAX_HOPS; i++) {
	    if (i==next_hop) {
	      newData->route[i] = TOS_NODE_ID;
	    }
	    else {
	      newData->route[i]=sMsg->route[i];
	    }
	  }
	  
	  memcpy(newData->packed_state_mask, sMsg->packed_state_mask,sizeof sMsg->packed_state_mask);
	  memcpy(newData->packed_state, sMsg->packed_state,sizeof sMsg->packed_state);
	  if (call StateForwarder.send(LEAF_CLUSTER_HEAD, &fwdMsg,  sizeof(fwdMsg))==SUCCESS){
	    sending = TRUE;
	  }
	}
      }
    }
  }


  //Receive a message repack and forward up to the next cluster head
  event message_t* StateReceiver.receive(message_t* msg,void* payload, uint8_t len) {
    StateMsg* sMsg;
    if (!call SMPool.empty() && call SMQueue.size() < call SMQueue.maxSize()) { 
      message_t *tmp = call SMPool.get();
      sMsg = (StateMsg*)payload;
      if (len == sizeof(sMsg)){
	call SMQueue.enqueue(sMsg);
	if (!sending) {
	  post SMForwardTask();
	}
	return tmp;
      }
    }  
    return msg; 
  }

  event void StateForwarder.sendDone(message_t *msg, error_t ok) {
    call SMPool.put(msg);
    if (! call ACKQueue.empty())
      post AckForwardTask();
    if (! call SMQueue.empty())
      post SMForwardTask();
    if (! call BNQueue.empty())
      post BNForwardTask();
    sending = FALSE;
  }


  //---------------- Deal with BN Message Forwarding---------------------

  task void BNForwardTask() { 
    StateMsg *newData;
    int i;
    int next_hop;
    StateMsg* sMsg;
    if (!call BNQueue.empty() && !sending) {
      sMsg = call BNQueue.dequeue();
      newData = call BNForwarder.getPayload(&fwdMsg,  sizeof(sMsg));
      if (newData != NULL) { 
	next_hop=(sMsg->hops)+1;
	if (next_hop<=MAX_HOPS){
	  newData->timestamp = sMsg->timestamp;
	  newData->special = sMsg->special;
	  newData->hops = next_hop;
	  
	  //loop through and pack the route adding this node on at the end
	  for (i = 0; i < MAX_HOPS; i++) {
	    if (i==next_hop) {
	      newData->route[i] = TOS_NODE_ID;
	    }
	    else {
	      newData->route[i]=sMsg->route[i];
	    }
	  }
	  
	  memcpy(newData->packed_state_mask, sMsg->packed_state_mask,sizeof sMsg->packed_state_mask);
	  memcpy(newData->packed_state, sMsg->packed_state,sizeof sMsg->packed_state);
	  if (call BNForwarder.send(LEAF_CLUSTER_HEAD, &fwdMsg,  sizeof(fwdMsg))==SUCCESS){
	    sending = TRUE;
	  }
	}
      }
    }
  }


  //Receive a message repack and forward up to the next cluster head
  event message_t* BNReceiver.receive(message_t* msg,void* payload, uint8_t len) {
    StateMsg* sMsg;
    if (!call BNPool.empty() && call BNQueue.size() < call BNQueue.maxSize()) { 
      message_t *tmp = call BNPool.get();
      sMsg = (StateMsg*)payload;
      if (len == sizeof(StateMsg)){
	call BNQueue.enqueue(sMsg);
	if (!sending) {
	  post BNForwardTask();
	}
	return tmp;
      }
    }  
    return msg;    
  }


  event void BNForwarder.sendDone(message_t *msg, error_t ok) {
    call BNPool.put(msg);
    if (! call ACKQueue.empty())
      post AckForwardTask();
    if (! call SMQueue.empty())
      post SMForwardTask();
    if (! call BNQueue.empty())
      post BNForwardTask();
    sending = FALSE;
  }
}
