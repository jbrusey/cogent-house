PFLAGS += -I%T/lib/net/ctp -I%T/lib/net -I%T/lib/net/4bitle
COMPONENT=RssiCogentRootC

PFLAGS += -DTOSH_DATA_LENGTH=118
CFLAGS += -DBLINKY
CFLAGS += -DRADIO_QUEUE_SIZE=15

ifneq ($(filter iris,$(MAKECMDGOALS)),) 
	CFLAGS += -DRF230_RSSI_ENERGY
endif

include $(MAKERULES)

