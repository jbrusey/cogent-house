#include "Sensor.h"
configuration DigitalC {
}
implementation {
	components DigitalP as App;
	components MainC;
	components LedsC;
	components HplMsp430InterruptP;
	components HplMsp430GeneralIOC as GIOC;
	components ActiveMessageC;
	components new AMSenderC(AM_RADIO_MODEL_MSG);

	App.Boot -> MainC;
	App.Leds -> LedsC;
	App.GIOIN -> GIOC.Port26;
	App.InputPin -> HplMsp430InterruptP.Port26; //set to read from gio3
	App.RadioControl -> ActiveMessageC;
	App.RadioReceive -> ActiveMessageC.Receive;
	App.AMSend -> AMSenderC;
	App.Packet -> AMSenderC;
}
