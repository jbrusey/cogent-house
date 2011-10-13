MIGPYFILES=$(addprefix cogent/node/,StateMsg.py ConfigMsg.py Packets.py) 
all: $(MIGPYFILES)


install:  $(MIGPYFILES)
	python setup.py install
	a2ensite cogent-house

 $(MIGPYFILES):
	make -C tos/Node telosb
