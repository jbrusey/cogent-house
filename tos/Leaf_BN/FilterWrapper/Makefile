PFLAGS += -I../ -I ../Kalman -I. -I ../AirQuality -I ../DEWMA

COMPONENT=DEWMAWrapperTestC
CFLAGS += -I$(TOSDIR)/lib/printf -Wall 
CFLAGS += -DPRINTF_BUFFER_SIZE=2048

include $(MAKERULES)

CC=gcc

test: test_mat22
	./test_mat22
