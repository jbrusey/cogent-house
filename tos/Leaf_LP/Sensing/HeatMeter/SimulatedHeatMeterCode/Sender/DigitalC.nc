configuration DigitalC {
}
implementation {
	components MainC;
	components LedsC;
	components DigitalP as App;
	components HplMsp430GeneralIOC as GIOC;
	components new TimerMilliC() as PulseTimer;
	components new TimerMilliC() as PulseEnd;

	App.Boot -> MainC;
	App.Leds -> LedsC;
	App.GIO -> GIOC.Port26;
	App.PulseTimer -> PulseTimer;
	App.PulseEnd -> PulseEnd;
}
