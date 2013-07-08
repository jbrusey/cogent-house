PFLAGS += -I./ -I../ -I%T/lib/net/ctp -I%T/lib/net -I%T/lib/net/4bitle -I%T/lib/net/drip -I./AirQuality -I./CurrentCost -I%T/lib/printf -I./PackState -I./AccessibleBitVector -I./HeatMeter -I./OptiSmart -I./WindowSensor -I./BlackBulb

COMPONENT=CogentHouseC

#Configuration
CFLAGS += -DCLUSTER_HEAD=0

# turn on leds for debugging?
# use "make telosb install.2 debug=1" to turn on debug
#ifdef debug
CFLAGS += -DBLINKY
CFLAGS += -DDEBUG
#endif

PFLAGS +=-DTOSH_DATA_LENGTH=76
#PFLAGS += -DCC2420_DEF_RFPOWER=3
CFLAGS += -DCC2420_DEF_CHANNEL=26


# default sensing period 307200 = 5 mins
CFLAGS += -DDEF_FIRST_PERIOD=10240
CFLAGS += -DDEF_SENSE_PERIOD=10240L
CFLAGS += -DDEF_BACKOFF_SENSE_PERIOD=10240
#CFLAGS += -DLEAF_TIMEOUT_TIME=61440L
CFLAGS += -DLEAF_TIMEOUT_TIME=8192L
CFLAGS += -DLOW_VOLTAGE=2.35

include $(MAKERULES)

