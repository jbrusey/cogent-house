PFLAGS += -I%T/lib/net/ctp -I%T/lib/net -I%T/lib/net/4bitle -I%T/lib/net/drip -I./AirQuality -I./CurrentCost -I%T/lib/printf -I./PackState -I./AccessibleBitVector -I./HeatMeter -I./OptiSmart -I./WindowSensor -I./BlackBulb
COMPONENT=CogentHouseC
PYTHON_TARGET_DIR=../../cogent/node
PYTHON_TGTS=$(addprefix $(PYTHON_TARGET_DIR)/,StateMsg.py StateV1Msg.py ConfigMsg.py Packets.py)
BUILD_EXTRA_DEPS += $(PYTHON_TGTS)
CLEAN_EXTRA += $(PYTHON_TGTS)

PFLAGS +=-DTOSH_DATA_LENGTH=106

# turn on leds for debugging?
#CFLAGS += -DBLINKY
#CFLAGS += -DDEBUG
# default sensing period 307200 = 5 mins
CFLAGS += -DDEF_SENSE_PERIOD=307200
CFLAGS += -DDEF_FIRST_PERIOD=30720

CFLAGS += -DLOW_POWER_LISTENING
CFLAGS += -DLPL_DEF_LOCAL_WAKEUP=1024
CFLAGS += -DLPL_DEF_REMOTE_WAKEUP=1024
CFLAGS += -DDELAY_AFTER_RECEIVE=20

include $(MAKERULES)

$(PYTHON_TARGET_DIR)/StateMsg.py: Packets.h
	mig python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< StateMsg -o $@

$(PYTHON_TARGET_DIR)/StateV1Msg.py: Packets.h
	mig python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< StateV1Msg -o $@

$(PYTHON_TARGET_DIR)/ConfigMsg.py: Packets.h
	mig python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< ConfigMsg -o $@

$(PYTHON_TARGET_DIR)/Packets.py: Packets.h PackState/packstate.h
	ncg python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< Packets.h -o $@

