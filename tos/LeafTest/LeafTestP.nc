// -*- c -*-

#include "Timer.h"
#include "Sensor.h"

module LeafTestP
{
  //setup and define the interfaces that will be used
  uses
    {
      interface Timer<TMilli> as MilliTimer;
      interface Boot;
      interface SplitControl as RadioControl;
      interface AMSend;
      interface Packet;
      interface LocalTime<TMilli>;
      interface Leds;
      interface Receive;
    }
}
implementation
{
  //set up global variables
  message_t packet;	//message_t is the message type sent between nodes
  radio_sense_msg_t* rsm; //pointer to mesage to be sent
  
  //Start the node
  event void Boot.booted()
  {
    call MilliTimer.startPeriodic(30240);
  }

  //When timer is fired get sensor readings, calc comfort and send result if there is a change
  event void MilliTimer.fired() {
    //start radio 
    call RadioControl.start();
  }
  
  //Packet has been sent
  event void AMSend.sendDone(message_t* bufPtr, error_t error) {
    //message sent stop radio 
    call RadioControl.stop();
  }
  
  //nothing needs to happen in these events
  event void RadioControl.stopDone(error_t err) {
  }


  event void RadioControl.startDone(error_t err) {

    call Leds.led1Toggle();
    //Set up packet radio_sense_msg_t def contained in header file
    rsm = (radio_sense_msg_t*)call Packet.getPayload(&packet, sizeof(radio_sense_msg_t));
      
    //make sure packet has been set up
    if (rsm == NULL) {return;}
    
    //pass all data
    rsm->node_id=TOS_NODE_ID;
    rsm->timestamp = call LocalTime.get();;
    call AMSend.send(DEF_CLUSTER_HEAD, &packet, sizeof(radio_sense_msg_t));
  }

 //receive sensing messages over the radio and forward to serial port
  event message_t* Receive.receive(message_t* bufPtr,void* payload, uint8_t len) {
    call Leds.led2Toggle();
  }
}

