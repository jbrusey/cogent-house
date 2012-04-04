PFLAGS += -I./AirQuality -I./CurrentCost -I%T/lib/printf -I./PackState -I./AccessibleBitVector -I./HeatMeter -I./Kalman -I./FilterWrapper -I./EventDetector -I./DEWMA -I./Exposure -I./ExposureEventDetector
COMPONENT=CogentHouseC

PYTHON_TARGET_DIR=../../cogent/node
PYTHON_TGTS=$(addprefix $(PYTHON_TARGET_DIR)/,StateMsg.py StateV1Msg.py ConfigMsg.py Packets.py AckMsg.py BNMsg.py)
BUILD_EXTRA_DEPS += $(PYTHON_TGTS)
CLEAN_EXTRA += $(PYTHON_TGTS)

PFLAGS +=-DTOSH_DATA_LENGTH=92
PFLAGS += -DCC2420_DEF_CHANNEL=18

# turn on leds for debugging?
#CFLAGS += -DBLINKY
#CFLAGS += -DDEBUG

CFLAGS += -DLEAF_CLUSTER_HEAD=1
CFLAGS += -DLEAF_MAX_RETRIES=3
CFLAGS += -DLEAF_TIMEOUT_TIME=30L


#CFLAGS += -DSS

CFLAGS += -DSIP  -DDEWMA #-DKALMAN
CFLAGS += -DSIP_TEMP_THRESH=0.25
CFLAGS += -DSIP_TEMP_ALPHA=0.2
CFLAGS += -DSIP_TEMP_BETA=0.2

CFLAGS += -DSIP_HUM_THRESH=1.
CFLAGS += -DSIP_HUM_ALPHA=0.1
CFLAGS += -DSIP_HUM_BETA=0.1

CFLAGS += -DSIP_CO2_THRESH=100.
CFLAGS += -DSIP_CO2_ALPHA=0.2
CFLAGS += -DSIP_CO2_BETA=0.2

CFLAGS += -DSIP_AQ_THRESH=0.1
CFLAGS += -DSIP_AQ_ALPHA=0.05
CFLAGS += -DSIP_AQ_BETA=0.05

CFLAGS += -DSIP_VOC_THRESH=100.
CFLAGS += -DSIP_VOC_ALPHA=0.05
CFLAGS += -DSIP_VOC_BETA=0.05


#CFLAGS += -DBN
CFLAGS += -DBN_GAMMA=0.9999868213
CFLAGS += -DBN_TEMP_BAND_THRESH=10.
CFLAGS += -DBN_HUM_BAND_THRESH=10.
CFLAGS += -DBN_CO2_BAND_THRESH=10.

# default sensing period 307200 = 5 mins
CFLAGS += -DDEF_SENSE_PERIOD=307200
include $(MAKERULES)


$(PYTHON_TARGET_DIR)/BNMsg.py: ../Packets.h
	mig python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< BNMsg -o $@
	
$(PYTHON_TARGET_DIR)/StateMsg.py: ../Packets.h
	mig python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< StateMsg -o $@

$(PYTHON_TARGET_DIR)/StateV1Msg.py: ../Packets.h
	mig python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< StateV1Msg -o $@

$(PYTHON_TARGET_DIR)/ConfigMsg.py: ../Packets.h
	mig python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< ConfigMsg -o $@

$(PYTHON_TARGET_DIR)/AckMsg.py: ../Packets.h
	mig python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< AckMsg -o $@

$(PYTHON_TARGET_DIR)/Packets.py: ../Packets.h PackState/packstate.h
	ncg python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< Packets.h -o $@

