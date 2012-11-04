PFLAGS += -I./AirQuality -I./CurrentCost -I%T/lib/printf -I./PackState -I./AccessibleBitVector -I./HeatMeter -I./Kalman -I./FilterWrapper -I./EventDetector -I./DEWMA -I./Exposure -I./ExposureEventDetector
COMPONENT=CogentHouseC

PFLAGS +=-DTOSH_DATA_LENGTH=110

# turn on leds for debugging?
#CFLAGS += -DBLINKY
#CFLAGS += -DDEBUG

# select node type
CFLAGS += -DLEAF
#CFLAGS += -DCLUSTER

CFLAGS += -DLEAF_CLUSTER_HEAD=40974L
CFLAGS += -DLEAF_MAX_RETRIES=3
CFLAGS += -DLEAF_TIMEOUT_TIME=10L

CFLAGS += -DHEARTBEAT_PERIOD=14688 #51 days

# default sensing period 307200 = 5 mins
CFLAGS += -DDEF_SENSE_PERIOD=307200L
CFLAGS += -DDEF_FIRST_PERIOD=10240

CFLAGS += -DBN_GAMMA=0.9999868213
CFLAGS += -DBN_TEMP_BAND_THRESH=10.
CFLAGS += -DBN_HUM_BAND_THRESH=10.
CFLAGS += -DBN_CO2_BAND_THRESH=10.

include $(MAKERULES)


