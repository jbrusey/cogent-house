CC=gcc
CFLAGS=-W -Wall -Wundef -Wstrict-prototypes -Wmissing-prototypes -Wmissing-declarations -O2

tests: test_poly
	./test_poly

test_poly: test_poly.o horner.o
	$(CC) $(CFLAGS) -o $@ test_poly.o horner.o