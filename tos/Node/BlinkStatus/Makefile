COMPONENT=BlinkStatusTestC

PFLAGS += -I .\
	-I ../../Util \
	-I %T/lib/printf \


ifdef debug
CFLAGS += -DDEBUG
endif

CFLAGS += -DBLINK_SECONDS=10

TINYOS_ROOT_DIR?=/opt/tinyos-main
include $(TINYOS_ROOT_DIR)/Makefile.include
