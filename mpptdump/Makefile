# http://www.gnu.org/software/make/manual/make.html
# http://www.cs.colby.edu/maxwell/courses/tutorials/maketutor/

CC = gcc
CFLAGS = -I.
LIBS =

mpptdump: mpptdump.c
	$(CC) $(CFLAGS) -o $@ $^ $(LIBS)

#######

.PHONY: clean

clean:
	rm -f *.o *~ core mpptdump
