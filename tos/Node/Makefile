PFLAGS += -I . -I ./Predict -I ./Heartbeat -I ./Filters/ -I ./Filters/DEWMA -I ./Filters/PassThrough -I./Sensing/Car  -I./Sensing/AirQuality -I./Sensing/Base -I./Sensing/OptiSmart  -I%T/lib/printf -I./PackState -I./AccessibleBitVector -I./FilterWrapper -I./EventDetector -I./SIPController  -I../Util/HashMap  -I%T/lib/net/ctp -I%T/lib/net -I../Util/ch4bitle -I../Util/HashMap -I./Exposure -I./BNController -I ./LowBatteryDetector  -I%T/lib/net/drip

COMPONENT=CogentHouseC

PYTHON_TARGET_DIR=../../cogent/node
PYTHON_TGTS=$(addprefix $(PYTHON_TARGET_DIR)/,StateMsg.py ConfigMsg.py Packets.py AckMsg.py)
BUILD_EXTRA_DEPS += $(PYTHON_TGTS)
CLEAN_EXTRA += $(PYTHON_TGTS)

#Configuration
CFLAGS += -DCLUSTER_HEAD=0
CFLAGS += -DSIP

# turn on leds for debugging?
#CFLAGS += -DBLINKY
#CFLAGS += -DDEBUG

PFLAGS +=-DTOSH_DATA_LENGTH=145
#PFLAGS += -DCC2420_DEF_RFPOWER=3
CFLAGS += -DCC2420_DEF_CHANNEL=21

CFLAGS += -DHEARTBEAT_MULTIPLIER=1L #7 hours SIP #51 days BN
CFLAGS += -DHEARTBEAT_PERIOD=1843200L #3686400L #1 hour  88473600 #1 day

# default sensing period 307200=5 mins
CFLAGS += -DDEF_FIRST_PERIOD=10240
CFLAGS += -DDEF_SENSE_PERIOD=2048L
CFLAGS += -DDEF_BACKOFF_SENSE_PERIOD=2048L

CFLAGS += -DLEAF_TIMEOUT_TIME=1024L
CFLAGS += -DLOW_VOLTAGE=2.35

CFLAGS += -DDEWMA 
CFLAGS += -DSIP_TEMP_MASK=1
CFLAGS += -DSIP_TEMP_THRESH=-1
CFLAGS += -DSIP_TEMP_ALPHA=1
CFLAGS += -DSIP_TEMP_BETA=1

CFLAGS += -DSIP_HUM_MASK=1
CFLAGS += -DSIP_HUM_THRESH=-1
CFLAGS += -DSIP_HUM_ALPHA=1
CFLAGS += -DSIP_HUM_BETA=1

CFLAGS += -DSIP_BATTERY_MASK=0
CFLAGS += -DSIP_BATTERY_THRESH=-1
CFLAGS += -DSIP_BATTERY_ALPHA=1
CFLAGS += -DSIP_BATTERY_BETA=1

CFLAGS += -DSIP_CO2_MASK=1
CFLAGS += -DSIP_CO2_THRESH=-1
CFLAGS += -DSIP_CO2_ALPHA=1
CFLAGS += -DSIP_CO2_BETA=1

CFLAGS += -DSIP_TEMPADC_MASK=1
CFLAGS += -DSIP_TEMPADC_THRESH=-1
CFLAGS += -DSIP_TEMPADC_ALPHA=1
CFLAGS += -DSIP_TEMPADC_BETA=1

CFLAGS += -DSIP_FLOW_MASK=1
CFLAGS += -DSIP_FLOW_THRESH=-1
CFLAGS += -DSIP_FLOW_ALPHA=1
CFLAGS += -DSIP_FLOW_BETA=1

CFLAGS += -DSIP_SOLAR_MASK=1
CFLAGS += -DSIP_SOLAR_THRESH=-1
CFLAGS += -DSIP_SOLAR_ALPHA=1
CFLAGS += -DSIP_SOLAR_BETA=1

CFLAGS += -DSIP_BLACKBULB_MASK=1
CFLAGS += -DSIP_BLACKBULB_THRESH=-1
CFLAGS += -DSIP_BLACKBULB_ALPHA=1
CFLAGS += -DSIP_BLACKBULB_BETA=1

include $(MAKERULES)

$(PYTHON_TARGET_DIR)/StateMsg.py: ../Packets.h
	mig python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< StateMsg -o $@

$(PYTHON_TARGET_DIR)/ConfigMsg.py: ../Packets.h
	mig python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< ConfigMsg -o $@

$(PYTHON_TARGET_DIR)/AckMsg.py: ../Packets.h
	mig python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< AckMsg -o $@

$(PYTHON_TARGET_DIR)/Packets.py: ../Packets.h PackState/packstate.h
	ncg python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< Packets.h -o $@

