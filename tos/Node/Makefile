PFLAGS += -I . -I ./Predict -I ./Heartbeat -I ./Filters/ -I ./Filters/DEWMA -I ./Filters/PassThrough  -I./Sensing/AirQuality -I./Sensing/Base -I./Sensing/WindowSensor -I./Sensing/TempADC -I./Sensing/PulseReader  -I./Sensing/ACStatus -I./Sensing/CurrentCost  -I%T/lib/printf -I./PackState -I./AccessibleBitVector -I./FilterWrapper -I./EventDetector -I./SIPController  -I../Util/HashMap  -I../Util  -I%T/lib/net/ctp -I%T/lib/net -I../Util/ch4bitle -I../Util/HashMap -I./Exposure -I./BNController -I ./LowBatteryDetector  -I./Sensing/BlackBulb -I%T/lib/net/drip

COMPONENT=CogentHouseC

PYTHON_TARGET_DIR=../../cogent/node
PYTHON_TGTS=$(addprefix $(PYTHON_TARGET_DIR)/,StateMsg.py ConfigMsg.py Packets.py AckMsg.py)
BUILD_EXTRA_DEPS += $(PYTHON_TGTS)
CLEAN_EXTRA += $(PYTHON_TGTS)

#Configuration
CFLAGS += -DSIP
#CFLAGS += -DBN

# turn on leds for debugging?
# use "make telosb install.2 debug=1" to turn on debug
ifdef debug
CFLAGS += -DBLINKY
CFLAGS += -DDEBUG
endif

PFLAGS +=-DTOSH_DATA_LENGTH=76
#PFLAGS += -DCC2420_DEF_RFPOWER=3
#CFLAGS += -DCC2420_DEF_CHANNEL=15

CFLAGS += -DHEARTBEAT_MULTIPLIER=7L #7 hours SIP #51 days BN
CFLAGS += -DHEARTBEAT_PERIOD=3686400L #3686400L #1 hour  88473600 #1 day

# default sensing period 307200 = 5 mins
CFLAGS += -DDEF_FIRST_PERIOD=10240
CFLAGS += -DDEF_SENSE_PERIOD=307200L
CFLAGS += -DDEF_BACKOFF_SENSE_PERIOD=307200L
CFLAGS += -DLEAF_TIMEOUT_TIME=10240L
CFLAGS += -DLOW_VOLTAGE=2.35

CFLAGS += -DDEWMA
CFLAGS += -DSIP_TEMP_MASK=1
CFLAGS += -DSIP_TEMP_THRESH=0.5
CFLAGS += -DSIP_TEMP_ALPHA=0.2
CFLAGS += -DSIP_TEMP_BETA=0.2

CFLAGS += -DSIP_TEMPADC_MASK=1
CFLAGS += -DSIP_TEMPADC_THRESH=0.5
CFLAGS += -DSIP_TEMPADC_ALPHA=0.2
CFLAGS += -DSIP_TEMPADC_BETA=0.2

CFLAGS += -DSIP_HUM_MASK=1
CFLAGS += -DSIP_HUM_THRESH=2.
CFLAGS += -DSIP_HUM_ALPHA=0.2
CFLAGS += -DSIP_HUM_BETA=0.2

CFLAGS += -DSIP_BATTERY_MASK=1
CFLAGS += -DSIP_BATTERY_THRESH=0.1
CFLAGS += -DSIP_BATTERY_ALPHA=0.05
CFLAGS += -DSIP_BATTERY_BETA=0.1

CFLAGS += -DSIP_CO2_MASK=1
CFLAGS += -DSIP_CO2_THRESH=100.
CFLAGS += -DSIP_CO2_ALPHA=0.2
CFLAGS += -DSIP_CO2_BETA=0.2

CFLAGS += -DSIP_BB_MASK=1
CFLAGS += -DSIP_BB_THRESH=0.0025
CFLAGS += -DSIP_BB_ALPHA=0.2
CFLAGS += -DSIP_BB_BETA=0.2

CFLAGS += -DSIP_AQ_MASK=1
CFLAGS += -DSIP_AQ_THRESH=0.1
CFLAGS += -DSIP_AQ_ALPHA=0.05
CFLAGS += -DSIP_AQ_BETA=0.05

CFLAGS += -DSIP_VOC_MASK=1
CFLAGS += -DSIP_VOC_THRESH=100.
CFLAGS += -DSIP_VOC_ALPHA=0.05
CFLAGS += -DSIP_VOC_BETA=0.05

CFLAGS += -DSIP_OPTI_MASK=1
CFLAGS += -DSIP_OPTI_THRESH=100 # units are 0.001 kWh
CFLAGS += -DSIP_OPTI_ALPHA=0
CFLAGS += -DSIP_OPTI_BETA=0

CFLAGS += -DSIP_CC_MASK=1
CFLAGS += -DSIP_CC_THRESH=50
CFLAGS += -DSIP_CC_ALPHA=0
CFLAGS += -DSIP_CC_BETA=0

CFLAGS += -DSIP_GAS_MASK=1
CFLAGS += -DSIP_GAS_THRESH=100
CFLAGS += -DSIP_GAS_ALPHA=0
CFLAGS += -DSIP_GAS_BETA=0

CFLAGS += -DSIP_HME_MASK=1
CFLAGS += -DSIP_HME_THRESH=1
CFLAGS += -DSIP_HME_ALPHA=0
CFLAGS += -DSIP_HME_BETA=0

CFLAGS += -DSIP_HMV_MASK=1
CFLAGS += -DSIP_HMV_THRESH=1
CFLAGS += -DSIP_HMV_ALPHA=0
CFLAGS += -DSIP_HMV_BETA=0

CFLAGS += -DSIP_WINDOW_MASK=1
CFLAGS += -DSIP_WINDOW_THRESH=1
CFLAGS += -DSIP_WINDOW_ALPHA=0
CFLAGS += -DSIP_WINDOW_BETA=0

CFLAGS += -DBN_GAMMA=0.9999868213
CFLAGS += -DBN_TEMP_BAND_THRESH=5.
CFLAGS += -DBN_HUM_BAND_THRESH=5.
CFLAGS += -DBN_CO2_BAND_THRESH=5.
CFLAGS += -DBN_VOC_BAND_THRESH=5.
CFLAGS += -DBN_AQ_BAND_THRESH=5.

include $(MAKERULES)

$(PYTHON_TARGET_DIR)/StateMsg.py: ../Packets.h
	mig python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< StateMsg -o $@

$(PYTHON_TARGET_DIR)/ConfigMsg.py: ../Packets.h
	mig python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< ConfigMsg -o $@

$(PYTHON_TARGET_DIR)/AckMsg.py: ../Packets.h
	mig python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< AckMsg -o $@

$(PYTHON_TARGET_DIR)/Packets.py: ../Packets.h PackState/packstate.h
	ncg python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< Packets.h -o $@

