PFLAGS += -I./ErrorDisplay \
	-I%T/lib/net/ctp \
	-I%T/lib/net \
	-I%T/lib/net/drip \
	-I%T/lib/net/4bitle #-I../Util/ch4bitle 

COMPONENT=RssiCogentRootC

PFLAGS += -DTOSH_DATA_LENGTH=76
CFLAGS += -DSERIAL_QUEUE_SIZE=50

CFLAGS += -DACK_TIMEOUT_TIME=5120L

#CFLAGS += -DCC2420_DEF_CHANNEL=15
#PFLAGS += -DCC2420_DEF_RFPOWER=3

#CFLAGS += -DBLINKY

include $(MAKERULES)

