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
	initialize_cogent_db
	alembic -c cogent/alembic.ini upgrade head

 $(MIGPYFILES): tos/Packets.h
	make -C tos/Node telosb
