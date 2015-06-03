COMPONENT=BootMessageTestC

PFLAGS += -I .\
	-I ../../Util \
	-I %T/lib/printf \
	-I %T/lib/net \
	-I %T/lib/net/ctp \
	-I %T/lib/net/4bitle

CFLAGS+=-DVC_REVISION="test string"
CFLAGS+=-DBOOT_TIMEOUT_TIME=20000

ifdef debug
CFLAGS += -DDEBUG
endif



include $(MAKERULES)
