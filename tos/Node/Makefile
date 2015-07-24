PFLAGS += -I . \
	-I %T/lib/net \
	-I %T/lib/net/ctp \
	-I %T/lib/net/drip \
	-I %T/lib/printf \
	-I .. \
	-I ../Util  \
	-I ../Util/HashMap  \
	-I ./AccessibleBitVector \
	-I ./BootMessage \
	-I ./BlinkStatus \
	-I ./EventDetector \
	-I ./FilterWrapper \
	-I ./Filters/ \
	-I ./Filters/DEWMA \
	-I ./Filters/PassThrough  \
	-I ./Heartbeat \
	-I ./PackState \
	-I ./Predict \
	-I ./SIPController  \
	-I ./Sensing \
	-I ./Sensing/Base \
        -I ./Sensing/Analog \
	-I ./Sensing/PolyClass \
	-I ./Sensing/PulseReader  \

# needed to allow packet to be defined in BootMessage
CFLAGS += -I ./BootMessage 

# use "make telosb install.2 cluster_based=1" to turn on cluster-based code

ifdef cluster_based
PFLAGS += -I ../Util/ch4bitle
BUILD_EXTRA_DEPS += ../Util/ch4bitle/LinkEstimatorP.nc
CFLAGS += -DCLUSTER_BASED
else #lpl based
PFLAGS += -I %T/lib/net/4bitle
CFLAGS += -DLOW_POWER_LISTENING
CFLAGS += -DLPL_DEF_LOCAL_WAKEUP=1024
CFLAGS += -DLPL_DEF_REMOTE_WAKEUP=1024
CFLAGS += -DDELAY_AFTER_RECEIVE=20
endif

COMPONENT=CogentHouseC

PYTHON_TARGET_DIR=../../pulp/node
PYTHON_TGTS=$(addprefix $(PYTHON_TARGET_DIR)/,StateMsg.py BootMsg.py ConfigMsg.py Packets.py AckMsg.py)
TOSMAKE_PRE_EXE_DEPS = $(PYTHON_TGTS)
TOSMAKE_CLEAN_EXTRA = $(PYTHON_TGTS)

#Configuration
# turn on leds for debugging?
# use "make telosb install.2 debug=1" to turn on debug
ifdef debug
CFLAGS += -DBLINKY
CFLAGS += -DDEBUG
endif

# if ac-powered node does not have ac-sensor but should still act as a
# cluster-head use "make ... missing_ac_sensor=1"
ifdef missing_ac_sensor
CFLAGS += -DMISSING_AC_SENSOR
endif

# radio channel
# use "make ... rf_channel=19" to get a radio channel of 19
ifdef rf_channel
CFLAGS += -DCC2420_DEF_CHANNEL=$(rf_channel)
endif

REVISION=$(shell git rev-parse --short HEAD)
CFLAGS+=-DVC_REVISION="$(REVISION)"

PFLAGS +=-DTOSH_DATA_LENGTH=76

CFLAGS += -DHEARTBEAT_MULTIPLIER=7L #7 hours SIP 
CFLAGS += -DHEARTBEAT_PERIOD=3686400L #3686400L #1 hour  88473600 #1 day

# default sensing period 307200 = 5 mins
CFLAGS += -DDEF_FIRST_PERIOD=10240
CFLAGS += -DDEF_SENSE_PERIOD=307200L
CFLAGS += -DLEAF_TIMEOUT_TIME=10240L
CFLAGS += -DBOOT_TIMEOUT_TIME=20480L
CFLAGS += -DBLINK_SECONDS=60
CFLAGS += -DLOW_VOLTAGE=2.35

CFLAGS += -DSIP_TEMP_MASK=1
CFLAGS += -DSIP_TEMP_THRESH=-1 # Disable SIP
CFLAGS += -DSIP_TEMP_ALPHA=0.2
CFLAGS += -DSIP_TEMP_BETA=0.2

CFLAGS += -DSIP_HUM_MASK=1
CFLAGS += -DSIP_HUM_THRESH=2.
CFLAGS += -DSIP_HUM_ALPHA=0.2
CFLAGS += -DSIP_HUM_BETA=0.2

CFLAGS += -DSIP_PAR_MASK=1
CFLAGS += -DSIP_PAR_THRESH=2.
CFLAGS += -DSIP_PAR_ALPHA=0.2
CFLAGS += -DSIP_PAR_BETA=0.2

CFLAGS += -DSIP_TSR_MASK=1
CFLAGS += -DSIP_TSR_THRESH=2.
CFLAGS += -DSIP_TSR_ALPHA=0.2
CFLAGS += -DSIP_TSR_BETA=0.2

CFLAGS += -DSIP_VOLTAGE_MASK=1
CFLAGS += -DSIP_VOLTAGE_THRESH=2.
CFLAGS += -DSIP_VOLTAGE_ALPHA=0.2
CFLAGS += -DSIP_VOLTAGE_BETA=0.2

CFLAGS += -DSIP_ADC_0_MASK=1
CFLAGS += -DSIP_ADC_0_THRESH=2.
CFLAGS += -DSIP_ADC_0_ALPHA=0.2
CFLAGS += -DSIP_ADC_0_BETA=0.2

CFLAGS += -DSIP_ADC_1_MASK=1
CFLAGS += -DSIP_ADC_1_THRESH=2.
CFLAGS += -DSIP_ADC_1_ALPHA=0.2
CFLAGS += -DSIP_ADC_1_BETA=0.2

CFLAGS += -DSIP_ADC_2_MASK=1
CFLAGS += -DSIP_ADC_2_THRESH=2.
CFLAGS += -DSIP_ADC_2_ALPHA=0.2
CFLAGS += -DSIP_ADC_2_BETA=0.2

CFLAGS += -DSIP_ADC_3_MASK=1
CFLAGS += -DSIP_ADC_3_THRESH=2.
CFLAGS += -DSIP_ADC_3_ALPHA=0.2
CFLAGS += -DSIP_ADC_3_BETA=0.2

CFLAGS += -DSIP_ADC_6_MASK=1
CFLAGS += -DSIP_ADC_6_THRESH=2.
CFLAGS += -DSIP_ADC_6_ALPHA=0.2
CFLAGS += -DSIP_ADC_6_BETA=0.2

CFLAGS += -DSIP_ADC_7_MASK=1
CFLAGS += -DSIP_ADC_7_THRESH=2.
CFLAGS += -DSIP_ADC_7_ALPHA=0.2
CFLAGS += -DSIP_ADC_7_BETA=0.2

CFLAGS += -DSIP_GIO2_MASK=1
CFLAGS += -DSIP_GIO2_THRESH=2.
CFLAGS += -DSIP_GIO2_ALPHA=0.2
CFLAGS += -DSIP_GIO2_BETA=0.2

CFLAGS += -DSIP_GIO3_MASK=1
CFLAGS += -DSIP_GIO3_THRESH=2.
CFLAGS += -DSIP_GIO3_ALPHA=0.2
CFLAGS += -DSIP_GIO3_BETA=0.2


TINYOS_ROOT_DIR?=/opt/tinyos-main
include $(TINYOS_ROOT_DIR)/Makefile.include


$(PYTHON_TARGET_DIR)/StateMsg.py: ../Packets.h
	nescc-mig python $(NESC_PFLAGS) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< StateMsg -o $@

$(PYTHON_TARGET_DIR)/BootMsg.py: ../Packets.h
	nescc-mig python $(NESC_PFLAGS) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< BootMsg -o $@

$(PYTHON_TARGET_DIR)/ConfigMsg.py: ../Packets.h
	nescc-mig python $(NESC_PFLAGS) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< ConfigMsg -o $@

$(PYTHON_TARGET_DIR)/AckMsg.py: ../Packets.h
	nescc-mig python $(NESC_PFLAGS) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< AckMsg -o $@

$(PYTHON_TARGET_DIR)/Packets.py: ../Packets.h PackState/packstate.h
	nescc-ncg python $(NESC_PFLAGS) $(CFLAGS) -python-classname=$(notdir $(basename $@)) $< Packets.h -o $@

../Util/ch4bitle/LinkEstimatorP.nc: ../Util/ch4bitle.patch
	-rm -rf ../Util/ch4bitle
	cp -r $(TOSROOT)/tos/lib/net/4bitle ../Util/ch4bitle
	(cd ../Util/ch4bitle/ && patch -p0) < $<
