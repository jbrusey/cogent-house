COMPONENT=PulseReaderTestC
PFLAGS += -I ../../../Util \
	-I %T/lib/printf 
ifdef debug
CFLAGS += -DDEBUG
endif
#CFLAGS += -W -Wall -Wundef -Wstrict-prototypes -Wmissing-prototypes -Wmissing-declarations -O2

TINYOS_ROOT_DIR?=/opt/tinyos-main
include $(TINYOS_ROOT_DIR)/Makefile.include
