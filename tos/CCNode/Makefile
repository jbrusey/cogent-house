PFLAGS += -I./ -I../ -I%T/lib/net/ctp -I%T/lib/net -I%T/lib/net/4bitle -I%T/lib/net/drip -I./AirQuality -I./CurrentCost -I%T/lib/printf -I./PackState -I./AccessibleBitVector -I./HeatMeter -I./OptiSmart -I./WindowSensor -I./BlackBulb



COMPONENT=CogentHouseC
PFLAGS +=-DTOSH_DATA_LENGTH=106

# turn on leds for debugging?
#CFLAGS += -DBLINKY
#CFLAGS += -DDEBUG
# default sensing period 307200 = 5 mins
CFLAGS += -DDEF_SENSE_PERIOD=307200
CFLAGS += -DDEF_FIRST_PERIOD=30720

CFLAGS += -DLOW_POWER_LISTENING
CFLAGS += -DLPL_DEF_LOCAL_WAKEUP=0
CFLAGS += -DLPL_DEF_REMOTE_WAKEUP=0
CFLAGS += -DDELAY_AFTER_RECEIVE=20

include $(MAKERULES)

