PFLAGS += -I../ -I ../../FilterWrapper -I ../../SIPController -I ../../Predict \
	-I../../../Util

COMPONENT=DEWMATestC
CFLAGS += -I$(TOSDIR)/lib/printf -Wall 

CFLAGS += -DRS_SIZE=10
CFLAGS += -DPRINTF_BUFFER_SIZE=2048
CFLAGS += -DDEF_SENSE_PERIOD=307200L

TINYOS_ROOT_DIR?=/opt/tinyos-main
include $(TINYOS_ROOT_DIR)/Makefile.include
