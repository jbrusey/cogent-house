PFLAGS += -I./AirQuality -I./CurrentCost -I%T/lib/printf -I./PackState -I./AccessibleBitVector -I./HeatMeter
COMPONENT=CogentHouseC

PYTHON_TARGET_DIR=../../cogent/node
PYTHON_TGTS=$(addprefix $(PYTHON_TARGET_DIR)/,StateMsg.py ConfigMsg.py Packets.py AckMsg.py BNMsg.py)

PFLAGS +=-DTOSH_DATA_LENGTH=118

# turn on leds for debugging?
#CFLAGS += -DBLINKY
CFLAGS += -DDEBUG

CFLAGS += -DLEAF_CLUSTER_HEAD=40974L
CFLAGS += -DRADIO_QUEUE_SIZE=10


include $(MAKERULES)


