#include <ctype.h>	// for isprint
#include <stdio.h>	// for sprintf, printf
#include <string.h>	// for strerror, strlen, index, strncmp, strncpy, strcmp
#include <stdlib.h>	// for strol, strtod
#include <unistd.h>	// for close, read, getopt
#include <fcntl.h>	// for open, fcntl, O_RDWR, O_NOCTTY, O_NONBLOCK, F_SETFL
#include <sys/ioctl.h>	// for ioctl
#include <errno.h>	// for errno
#include <termios.h>	// for struct termios, tcgetattr, cfmakeraw, cfsetspeed, tcsetattr, VMIN, VTIMES, CSB, tcdrain
#include <sysexits.h>	// for EX_IOERR, EX_OK
#include <sys/param.h>	// for MAXPATHLEN
#include <time.h>	// for ctime, time
#include <signal.h>	// for sigaction

#define VERSION "v1.00"

static int openSerialPort(const char *bsdPath);static int openSerialPort(const char *bsdPath);
static int readSerialData (int fileDescriptor, int bCont);
static void closeSerialPort(int fileDescriptor);

// keep running until user hits Ctrl-C (also obviously works if only one frame to be printed)
volatile int keepRunning = 1;

// Hold the original termios attributes so we can reset them
static struct termios gOriginalTTYAttrs;

// http://www.victronenergy.com/upload/documents/VE.Direct%20Protocol.pdf
struct mppt {
	int pid;	// product ID
	int fw;		// firmware version
	char ser[16];	// serial number
	int v;		// main (battery) voltage [mV]
	int i;		// main (battery) charging current [mA]
	int il;		// load current [mA]				fw v1.15
	int vpv;	// panel voltage [mV]
	int ppv;	// panel power [W]
	int cs;		// converter state
	int err;	// error state
	int load;	// load switch state (1=ON, 0=OFF)		fw v1.12
	int yield_total;	// yield total (H19) [0.01kWh]
	int yield_today;	// yield today (H20) [0.01kWh]
	int yield_yesterday;	// yield yesterday (H22) [0.01kWh]
	int maxpower_today;	// maximum power today (H21) [W]
	int maxpower_yesterday;	// maximum power yesterday (H23) [W]
	int hsds;		// daty sequence number			fw v1.16
} mppt;
