#include <Timer.h>
#include "Sensor.h"

#define TIMER_PERIOD_MILLI 200

module DigitalP {
	uses interface Boot;
	uses interface Leds;
	uses interface HplMsp430GeneralIO as GIOIN;
	uses interface HplMsp430Interrupt as InputPin;
	uses interface SplitControl as RadioControl;
	uses interface AMSend;
	uses interface Packet;
	uses interface Receive as RadioReceive[am_id_t id];
}

implementation {
	message_t packet;	//message_t is the message type sent between nodes

	event void Boot.booted() {
		call InputPin.clear();
		call InputPin.enable();
		call InputPin.edge(FALSE);
		call GIOIN.makeInput(); //make it input
		//start radio
		call RadioControl.start();
	}

	async event void InputPin.fired() {
		radio_model_msg_t* rcm;

		//toggle led to get counts
		call Leds.led2Toggle();
		
		//clear the interrupt pending flag
		call InputPin.clear();

		//send

		rcm = (radio_model_msg_t*)(call Packet.getPayload(&packet, sizeof(radio_model_msg_t)));
		if (rcm == NULL) {return;}
		rcm->trigger = 1;
		call AMSend.send(0, &packet, sizeof(radio_model_msg_t));
	}

	event void RadioControl.startDone(error_t err) {}
	event void AMSend.sendDone(message_t* bufPtr, error_t error) {}
	event void RadioControl.stopDone(error_t err) {}
	event message_t *RadioReceive.receive[am_id_t id](message_t *msg,void *payload,uint8_t len) {}

}
