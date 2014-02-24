PFLAGS += -I . -I .. -I ../FilterWrapper -I ../Kalman \
	-I ../Sensing/Base -I ../Sensing/AirQuality \
	-I ../Filters/DEWMA -I ../Predict -I ../Heartbeat \
	-I ../Filters/. -I ../Filters/PassThrough -I ../../Util \
	-I ../Sensing/PulseReader

COMPONENT=ControllerTestC
CFLAGS += -I$(TOSDIR)/lib/printf -Wall 
CFLAGS += -DPRINTF_BUFFER_SIZE=2048
CFLAGS += -DDEF_SENSE_PERIOD=10240
ifdef debug
CFLAGS += -DDEBUG
endif
include $(MAKERULES)

