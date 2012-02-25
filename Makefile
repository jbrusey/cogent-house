#
# cogent-house
# 
# Use this to install by going:
#    make all
#    sudo make install
.PHONY: all install

MIGPYFILES=$(addprefix cogent/node/,StateMsg.py ConfigMsg.py Packets.py) 
all: $(MIGPYFILES)

install:  all
	python setup.py install
	a2ensite cogent-house
	(cd cogent && alembic upgrade head)

 $(MIGPYFILES): tos/Node/Packets.h
	make -C tos/Node telosb
