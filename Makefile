all:
	echo "did you mean make install?"

install:
	python setup.py install
	a2ensite cogent-house