COMPONENT=BlinkStatusTestC

PFLAGS += -I .\
	-I ../../Util \
	-I %T/lib/printf \


ifdef debug
CFLAGS += -DDEBUG
endif

CFLAGS += -DBLINK_SECONDS=10



include $(MAKERULES)
