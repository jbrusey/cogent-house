PFLAGS += -I./AirQuality -I./CurrentCost -I%T/lib/printf -I./PackState -I./AccessibleBitVector -I./HeatMeter -I./Kalman -I./FilterWrapper -I./EventDetector -I./DEWMA -I%T/lib/net/ctp -I%T/lib/net -I%T/lib/net/4bitle -I../Util/HashMap
COMPONENT=CogentHouseC


PFLAGS +=-DTOSH_DATA_LENGTH=118
#CFLAGS += -DCC2420_DEF_RFPOWER=1

PYTHON_TARGET_DIR=../../cogent/node
PYTHON_TGTS=$(addprefix $(PYTHON_TARGET_DIR)/,StateMsg.py ConfigMsg.py Packets.py AckMsg.py BNMsg.py)
BUILD_EXTRA_DEPS += $(PYTHON_TGTS)
CLEAN_EXTRA += $(PYTHON_TGTS)

# turn on leds for debugging?
#CFLAGS += -DBLINKY
CFLAGS += -DDEBUG

#ACK queue and hash maps sizes
CFLAGS += -DRADIO_QUEUE_SIZE=15
CFLAGS += -DHASH_SIZE=19

#time out time in seconds
CFLAGS += -DLEAF_TIMEOUT_TIME=5120L

# default sensing period 307200 = 5 mins
CFLAGS += -DDEF_FIRST_PERIOD=10240
CFLAGS += -DDEF_SENSE_PERIOD=10240L
CFLAGS += -DDEF_BACKOFF_SENSE_PERIOD=10240L

CFLAGS += -DCLUSTER_HEAD=0
CFLAGS += -DHEARTBEAT_PERIOD=89 #7 hours

CFLAGS += -DSIP  -DDEWMA #-DKALMAN
CFLAGS += -DSIP_TEMP_THRESH=0.0
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

include $(MAKERULES)


$(PYTHON_TARGET_DIR)/StateMsg.py: ../Packets.h
	mig python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< StateMsg -o $@

$(PYTHON_TARGET_DIR)/BNMsg.py: ../Packets.h
	mig python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< BNMsg -o $@

$(PYTHON_TARGET_DIR)/ConfigMsg.py: ../Packets.h
	mig python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< ConfigMsg -o $@

$(PYTHON_TARGET_DIR)/AckMsg.py: ../Packets.h
	mig python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< AckMsg -o $@

$(PYTHON_TARGET_DIR)/Packets.py: ../Packets.h PackState/packstate.h
	ncg python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< Packets.h -o $@



