PFLAGS += -I%T/lib/net/ctp -I%T/lib/net -I%T/lib/net/4bitle
COMPONENT=RssiCogentRootC

PFLAGS += -DTOSH_DATA_LENGTH=175
CFLAGS += -DBLINKY
CFLAGS += -DRADIO_QUEUE_SIZE=13

ifneq ($(filter iris,$(MAKECMDGOALS)),) 
	CFLAGS += -DRF230_RSSI_ENERGY
endif

include $(MAKERULES)

