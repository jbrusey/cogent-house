PFLAGS += -I . -I ../Sensing/Base -I ../Sensing/AirQuality -I ../Filters/. -I ../Filters/DEWMA -I ../Predict  -I ../SIPController -I ../../Util

COMPONENT=DEWMAWrapperTestC
CFLAGS += -I$(TOSDIR)/lib/printf -Wall 
CFLAGS += -DPRINTF_BUFFER_SIZE=2048
CFLAGS += -DDEF_SENSE_PERIOD=1024

include $(MAKERULES)

CC=gcc

