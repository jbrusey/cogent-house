PFLAGS += -I./ErrorDisplay \
	-I%T/lib/net/ctp \
	-I%T/lib/net \
	-I%T/lib/net/drip \
	-I%T/lib/net/4bitle

COMPONENT=RssiCogentRootC

PFLAGS += -DTOSH_DATA_LENGTH=76
CFLAGS += -DSERIAL_QUEUE_SIZE=50

CFLAGS += -DACK_TIMEOUT_TIME=5120L

#ifdef cluster_based
#else
CFLAGS += -DLOW_POWER_LISTENING
CFLAGS += -DLPL_DEF_LOCAL_WAKEUP=0
CFLAGS += -DLPL_DEF_REMOTE_WAKEUP=1024
CFLAGS += -DDELAY_AFTER_RECEIVE=20
#endif

# radio channel
# use "make ... rf_channel=19" to get a radio channel of 19
ifdef rf_channel
CFLAGS += -DCC2420_DEF_CHANNEL=$(rf_channel)
endif

include $(MAKERULES)

