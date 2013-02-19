PFLAGS += -I./AirQuality -I./CurrentCost -I%T/lib/printf -I./PackState -I./AccessibleBitVector  -I%T/lib/net/ctp -I%T/lib/net -I%T/lib/net/4bitle -I%T/lib/net/drip -I../Util/HashMap
COMPONENT=CogentHouseC

PFLAGS +=-DTOSH_DATA_LENGTH=175

PYTHON_TARGET_DIR=../../cogent/node
PYTHON_TGTS=$(addprefix $(PYTHON_TARGET_DIR)/,StateMsg.py ConfigMsg.py Packets.py AckMsg.py)
BUILD_EXTRA_DEPS += $(PYTHON_TGTS)
CLEAN_EXTRA += $(PYTHON_TGTS)

# turn on leds for debugging?
#CFLAGS += -DBLINKY
#CFLAGS += -DDEBUG

#CFLAGS += -DCC2420_DEF_CHANNEL=15

# default sensing period 307200 = 5 mins
CFLAGS += -DDEF_FIRST_PERIOD=10240
CFLAGS += -DDEF_SENSE_PERIOD=307200L
CFLAGS += -DDEF_BACKOFF_SENSE_PERIOD=307200L

#LPL setup cluster head =1 low powert options uncommented
CFLAGS += -DCLUSTER_HEAD=1

#ACK queue and hash maps sizes
CFLAGS += -DRADIO_QUEUE_SIZE=15
CFLAGS += -DHASH_SIZE=19

include $(MAKERULES)


$(PYTHON_TARGET_DIR)/StateMsg.py: ../Packets.h
	mig python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< StateMsg -o $@

$(PYTHON_TARGET_DIR)/ConfigMsg.py: ../Packets.h
	mig python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< ConfigMsg -o $@

$(PYTHON_TARGET_DIR)/AckMsg.py: ../Packets.h
	mig python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< AckMsg -o $@

$(PYTHON_TARGET_DIR)/Packets.py: ../Packets.h PackState/packstate.h
	ncg python -target=$(PLATFORM) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< Packets.h -o $@

