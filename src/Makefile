CC = clang
CFLAGS = -O2 -Wall -fPIC
LDFLAGS = -shared

TARGET = librules.dylib

all: $(TARGET)

$(TARGET): rules.o
	$(CC) $(LDFLAGS) -o $@ $^

rules.o: rules.c rules.h
	$(CC) $(CFLAGS) -c rules.c

clean:
	rm -f *.o $(TARGET)
