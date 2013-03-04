// -*- c -*- 

generic module HeartbeatC(uint8_t mult, uint32_t p)@safe()
{
  provides interface Heartbeat;
  uses interface Timer<TMilli> as HeartbeatTimer;
}
implementation
{
  uint32_t period = p;
  uint8_t resetMult = mult;
  uint8_t periodsToHeartbeat = mult;
  bool initialised = FALSE;
  
  //Where will this be called?
  command void Heartbeat.init(){
    if (!initialised)
      call HeartbeatTimer.startOneShot(period);
      initialised=TRUE;
  }

  //Decrease periods if period > 0
  event void HeartbeatTimer.fired(){
    if (periodsToHeartbeat > 0){
	  periodsToHeartbeat=periodsToHeartbeat-1;
   	  call HeartbeatTimer.startOneShot(period);
    }
    else //should not trigger
      periodsToHeartbeat = 0;
  }
  
  //Reset heartbeat period
  command void Heartbeat.reset(){
    if (initialised)
      periodsToHeartbeat = mult; 
      call HeartbeatTimer.startOneShot(period);
  }
  
  //Return TRUE if a Heartbeat needs to be sent else return FALSE
  command bool Heartbeat.triggered(){
    if (periodsToHeartbeat==0 && initialised)
      return TRUE;
    else
      return FALSE;
  }
}

