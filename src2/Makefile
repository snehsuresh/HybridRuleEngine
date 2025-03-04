CC = clang
CFLAGS = -O3 -flto -Wall -fPIC -march=native -fopenmp
LDFLAGS = -shared -fopenmp

TARGET = librules.dylib

all: $(TARGET)

$(TARGET): rules.o
	$(CC) $(LDFLAGS) -o $@ $^

rules.o: rules.c rules.h
	$(CC) $(CFLAGS) -c rules.c

clean:
	rm -f *.o $(TARGET)
