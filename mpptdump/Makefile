# http://www.gnu.org/software/make/manual/make.html
# http://www.cs.colby.edu/maxwell/courses/tutorials/maketutor/

CC = gcc
CFLAGS = -I.

mpptdump: mpptdump.c
	$(CC) -o $@ $^ $(CFLAGS)

#######

.PHONY: clean

clean:
	rm -f *.o *~ core mpptdump
