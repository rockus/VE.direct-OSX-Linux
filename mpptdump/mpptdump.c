#include "mpptdump.h"

void intHandler(int sig) {
    keepRunning = 0;
}

int main(int argc, char **argv)
{
    char	deviceFilePath[MAXPATHLEN];
    int		fileDescriptor;
    int		c;
    int		bCont;	// flag for continuous operation
    struct sigaction act;

    opterr = 0;
    while ((c=getopt(argc, argv, "cd:h")) != -1) {
	switch (c) {
	    case 'c': bCont = 1; break;
	    case 'd': strcpy(deviceFilePath, optarg); break;
	    case 'h': printHelp(); return 1;
	    case '?': if (optopt=='d')
			fprintf(stderr, "Option -%c requires an argument.\n", optopt);
		      else if (isprint (optopt))
			fprintf(stderr, "Unknown option '-%c'.\n", optopt);
		      else
			fprintf(stderr, "Unknown option character '\\x%x'.\n", optopt);
		      return 1;
	    default: abort();
	}
    }

    act.sa_handler = intHandler;
    sigaction(SIGINT, &act, NULL);	// catch Ctrl-C

//printf ("dev: %s\n", deviceFilePath);

    if (!deviceFilePath[0])
    {
        printf("No serial device found. Did you specify the '-d /dev/device' option?\n");
        return EX_UNAVAILABLE;
    }

    fileDescriptor = openSerialPort(deviceFilePath);
    if (fileDescriptor == -1)
    {
        return EX_IOERR;
    }

    if (!(readSerialData(fileDescriptor, bCont))) {
        printf("Could not read data.\n");
    }

    closeSerialPort(fileDescriptor);
//    printf("Modem port closed.\n");
    return EX_OK;
}


// Given the path to a serial device, open the device and configure it.
// Return the file descriptor associated with the device.
static int openSerialPort(const char *bsdPath)
{
    int             fileDescriptor = -1;
    int             handshake;
    struct termios  options;
    
    // Open the serial port read/write, with no controlling terminal, and don't wait for a connection.
    // The O_NONBLOCK flag also causes subsequent I/O on the device to be non-blocking.
    // See open(2) <x-man-page://2/open> for details.
    
    fileDescriptor = open(bsdPath, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fileDescriptor == -1) {
        printf("Error opening serial port %s - %s(%d).\n",
               bsdPath, strerror(errno), errno);
        goto error;
    }
    
    // Note that open() follows POSIX semantics: multiple open() calls to the same file will succeed
    // unless the TIOCEXCL ioctl is issued. This will prevent additional opens except by root-owned
    // processes.
    // See tty(4) <x-man-page//4/tty> and ioctl(2) <x-man-page//2/ioctl> for details.
    
    if (ioctl(fileDescriptor, TIOCEXCL) == -1) {
        printf("Error setting TIOCEXCL on %s - %s(%d).\n",
               bsdPath, strerror(errno), errno);
        goto error;
    }

    // Now that the device is open, clear the O_NONBLOCK flag so subsequent I/O will block.
    // See fcntl(2) <x-man-page//2/fcntl> for details.

    if (fcntl(fileDescriptor, F_SETFL, 0) == -1) {
        printf("Error clearing O_NONBLOCK %s - %s(%d).\n",
               bsdPath, strerror(errno), errno);
        goto error;
    }

    // Get the current options and save them so we can restore the default settings later.

    if (tcgetattr(fileDescriptor, &gOriginalTTYAttrs) == -1) {
        printf("Error getting tty attributes %s - %s(%d).\n",
               bsdPath, strerror(errno), errno);
        goto error;
    }
    
    // The serial port attributes such as timeouts and baud rate are set by modifying the termios
    // structure and then calling tcsetattr() to cause the changes to take effect. Note that the
    // changes will not become effective without the tcsetattr() call.
    // See tcsetattr(4) <x-man-page://4/tcsetattr> for details.
    
    options = gOriginalTTYAttrs;
    
    // Print the current input and output baud rates.
    // See tcsetattr(4) <x-man-page://4/tcsetattr> for details.
    
//    printf("Current input baud rate is %d\n", (int) cfgetispeed(&options));
//    printf("Current output baud rate is %d\n", (int) cfgetospeed(&options));

    // Set raw input (non-canonical) mode, with reads blocking until either a single character
    // has been received or a one second timeout expires.
    // See tcsetattr(4) <x-man-page://4/tcsetattr> and termios(4) <x-man-page://4/termios> for details.
    
    cfmakeraw(&options);
    options.c_cc[VMIN] = 0;
    options.c_cc[VTIME] = 10;
    
    // The baud rate, word length, and handshake options can be set as follows:
    
    cfsetspeed(&options, B19200);       // Set 19200 baud
//    options.c_cflag |= (CS7        |    // Use 7 bit words
//                        PARENB     |    // Parity enable (even parity if PARODD not also set)
//                        CCTS_OFLOW |    // CTS flow control of output
//                        CRTS_IFLOW);    // RTS flow control of input
    options.c_cflag = CS8;

/*  
    // The IOSSIOSPEED ioctl can be used to set arbitrary baud rates
    // other than those specified by POSIX. The driver for the underlying serial hardware
    // ultimately determines which baud rates can be used. This ioctl sets both the input
    // and output speed.
    
    speed_t speed = 14400; // Set 14400 baud
    if (ioctl(fileDescriptor, IOSSIOSPEED, &speed) == -1) {
        printf("Error calling ioctl(..., IOSSIOSPEED, ...) %s - %s(%d).\n",
               bsdPath, strerror(errno), errno);
    }
*/
    // Print the new input and output baud rates. Note that the IOSSIOSPEED ioctl interacts with the serial driver
    // directly bypassing the termios struct. This means that the following two calls will not be able to read
    // the current baud rate if the IOSSIOSPEED ioctl was used but will instead return the speed set by the last call
    // to cfsetspeed.
    
//    printf("Input baud rate changed to %d\n", (int) cfgetispeed(&options));
//    printf("Output baud rate changed to %d\n", (int) cfgetospeed(&options));

    // Cause the new options to take effect immediately.

    if (tcsetattr(fileDescriptor, TCSANOW, &options) == -1) {
        printf("Error setting tty attributes %s - %s(%d).\n",
               bsdPath, strerror(errno), errno);
        goto error;
    }

    // To set the modem handshake lines, use the following ioctls.
    // See tty(4) <x-man-page//4/tty> and ioctl(2) <x-man-page//2/ioctl> for details.
/*
    // Assert Data Terminal Ready (DTR)
    if (ioctl(fileDescriptor, TIOCSDTR) == -1) {
        printf("Error asserting DTR %s - %s(%d).\n",
               bsdPath, strerror(errno), errno);
    }

    // Clear Data Terminal Ready (DTR)
    if (ioctl(fileDescriptor, TIOCCDTR) == -1) {
        printf("Error clearing DTR %s - %s(%d).\n",
               bsdPath, strerror(errno), errno);
    }
*/

    // Set the modem lines depending on the bits set in handshake
//    handshake = TIOCM_DTR | TIOCM_RTS | TIOCM_CTS | TIOCM_DSR;
    handshake = TIOCM_DTR;	// set DTR, clear RTS and all others
    if (ioctl(fileDescriptor, TIOCMSET, &handshake) == -1) {
        printf("Error setting handshake lines %s - %s(%d).\n",
               bsdPath, strerror(errno), errno);
    }

    // To read the state of the modem lines, use the following ioctl.
    // See tty(4) <x-man-page//4/tty> and ioctl(2) <x-man-page//2/ioctl> for details.
    // Store the state of the modem lines in handshake

    if (ioctl(fileDescriptor, TIOCMGET, &handshake) == -1) {
        printf("Error getting handshake lines %s - %s(%d).\n",
               bsdPath, strerror(errno), errno);
    }
    
//    printf("Handshake lines currently set to %04x\n", handshake);
/*
    unsigned long mics = 1UL;
    
    // Set the receive latency in microseconds. Serial drivers use this value to determine how often to
    // dequeue characters received by the hardware. Most applications don't need to set this value: if an
    // app reads lines of characters, the app can't do anything until the line termination character has been
    // received anyway. The most common applications which are sensitive to read latency are MIDI and IrDA
    // applications.
    
    if (ioctl(fileDescriptor, IOSSDATALAT, &mics) == -1) {
        // set latency to 1 microsecond
        printf("Error setting read latency %s - %s(%d).\n",
               bsdPath, strerror(errno), errno);
        goto error;
    }
*/    
    // Success
    return fileDescriptor;
    
    // Failure path
error:
    if (fileDescriptor != -1) {
        close(fileDescriptor);
    }
    
    return -1;
}

// Given the file descriptor for a serial device, close that device.
void closeSerialPort(int fileDescriptor)
{
    // Block until all written output has been sent from the device.
    // Note that this call is simply passed on to the serial device driver.
    // See tcsendbreak(3) <x-man-page://3/tcsendbreak> for details.
    if (tcdrain(fileDescriptor) == -1) {
        printf("Error waiting for drain - %s(%d).\n",
               strerror(errno), errno);
    }
    
    // Traditionally it is good practice to reset a serial port back to
    // the state in which you found it. This is why the original termios struct
    // was saved.
    if (tcsetattr(fileDescriptor, TCSANOW, &gOriginalTTYAttrs) == -1) {
        printf("Error resetting tty attributes - %s(%d).\n",
               strerror(errno), errno);
    }
    
    close(fileDescriptor);
}

// Read from serial port
int readSerialData (int fileDescriptor, int bCont)
{
    char	buffer[256];
    char	*bufPtr;
    ssize_t	numBytes;
    char	*valuePtr;
    int		found;
    int		checksum_line, checksum;
    int 	nParams, nFrames, nFramesOk, i, j, iMax;

    nFrames = 0;

//  iMax=1; if (bCont) {iMax=10;}
//  for (i=0; i<iMax; i++)
  do
  {

    for (nParams=0; nParams<17; nParams++)
    {
	bufPtr = buffer;	// init bufPtr, i.e. flush buffer
	found = 0;
	do {
	    numBytes = read(fileDescriptor, bufPtr, 1);	// read one char
	    bufPtr+=numBytes;
	} while (*(bufPtr-1) != '\n');	// new line

	// create checksum over whole line including \r\n
	*(bufPtr) = '\0';
	checksum_line=0;
	for (j=0; j<strlen(buffer); j++)
	{
	    checksum_line += buffer[j];
	}

	if (strlen(buffer) > 2) {			// only consider non-empty lines
	    *(bufPtr-2) = '\0';	// delete 0d0a (bufPtr points to first byte in buffer that is empty)
	    // buffer now contains one line of data, excluding 0d0a

	    valuePtr = index(buffer, '\t');		// pointer to delimiter
	    if (valuePtr) {				// only if delimiter found
		*(valuePtr) = '\0';				// overwrite delimiter with NUL terminator to terminate 'key' string
								// 'buffer' now only runs until end of 'key' string
		valuePtr++;					// point to after delimiter for 'value'


		if (!(strncmp(buffer,"PID",3))) {mppt.pid = strtol(valuePtr, NULL, 0);found=1; nParams=1; checksum=checksum_line; nFrames++;}
		if (!(strncmp(buffer,"FW", 2))) {mppt.fw = strtod(valuePtr, NULL); found=1; checksum += checksum_line;}
		if (!(strncmp(buffer,"SER#", 4))) {strncpy(mppt.ser, valuePtr, 16); found=1; checksum += checksum_line;}
		if (!(strcmp(buffer,"V"))) {mppt.v = strtod(valuePtr, NULL); found=1; checksum += checksum_line;}
		if (!(strcmp(buffer,"I"))) {mppt.i = strtod(valuePtr, NULL); found=1; checksum += checksum_line;}
		if (!(strncmp(buffer,"IL", 2))) {mppt.il = strtod(valuePtr, NULL); found=1; checksum += checksum_line;}		// fw v1.15
		if (!(strncmp(buffer,"VPV", 3))) {mppt.vpv = strtod(valuePtr, NULL); found=1; checksum += checksum_line;}
		if (!(strncmp(buffer,"PPV", 3))) {mppt.ppv = strtod(valuePtr, NULL); found=1; checksum += checksum_line;}
		if (!(strncmp(buffer,"CS", 3))) {mppt.cs = strtod(valuePtr, NULL); found=1; checksum += checksum_line;}
		if (!(strncmp(buffer,"ERR", 3))) {mppt.err = strtod(valuePtr, NULL); found=1; checksum += checksum_line;}
		if (!(strncmp(buffer,"LOAD", 4))) {mppt.load=0; if(!(strncmp(valuePtr,"ON",2))){mppt.load=1;} found=1; checksum += checksum_line;}	// fw v1.12
		if (!(strncmp(buffer,"H19", 3))) {mppt.yield_total = strtod(valuePtr, NULL); found=1; checksum += checksum_line;}
		if (!(strncmp(buffer,"H20", 3))) {mppt.yield_today = strtod(valuePtr, NULL); found=1; checksum += checksum_line;}
		if (!(strncmp(buffer,"H22", 3))) {mppt.yield_yesterday = strtod(valuePtr, NULL); found=1; checksum += checksum_line;}
		if (!(strncmp(buffer,"H21", 3))) {mppt.maxpower_today = strtod(valuePtr, NULL); found=1; checksum += checksum_line;}
		if (!(strncmp(buffer,"H23", 3))) {mppt.maxpower_yesterday = strtod(valuePtr, NULL); found=1; checksum += checksum_line;}
		if (!(strncmp(buffer,"HSDS", 4))) {mppt.hsds = strtod(valuePtr, NULL); found=1; checksum += checksum_line;}		// fw v1.16
//		if (!(strncmp(buffer,"Checksum", 8))) {printf("checksum ignored for now. char: %x\n", (int)*valuePtr & 0xff); found=1; checksum += checksum_line;}
		if (!(strncmp(buffer,"Checksum", 8))) {found=1; checksum += checksum_line;}

//		if (!found) {printf("undefined field: %s:%s\n", buffer, valuePtr);}	// buffer == key	// print undefined keys

//		if (found) printf ("%d:%02x:%02x\n", nParams, checksum_line, checksum);
		if (nParams>=16 && checksum&0xff && mppt.ser[0]=='\0') {nParams=1;}	// repeat if checksum != 0 and no ser number;
	    }
	}
    }

    printf ("\x1b[2J\x1b[1;1H");	// clear screen

    printf ("\033[2;3H");		// move cursor to line 2, col 3
    printf ("%s %s %s", TOOLNAME, VERSION, COPYRIGHT);

    printf ("\n\n  date : ");
    time_t mytime; mytime = time(NULL); printf("%s", ctime(&mytime));

    printf ("  frame: %d\n\n", nFrames);

    printf ("charger:\n");
//    printf ("pid : 0x%04X\n", mppt.pid);
    switch (mppt.pid) {
	case 0x300: printf ("  type: MPPT 70/15 (PID 0x300)\n");break;
	case 0xa042: printf ("  type: MPPT 75/15 (PID 0xA042)\n");break;
	case 0xa043: printf ("  type: MPPT 100/15 (PID 0xA043)\n");break;
	case 0xa044: printf ("  type: MPPT 100/30 (PID 0xA044)\n");break;
	case 0xa041: printf ("  type: MPPT 150/35 (PID 0xA041)\n");break;
	case 0xa040: printf ("  type: MPPT 75/50 (PID 0xA040)\n");break;
	case 0xa045: printf ("  type: MPPT 100/50 (PID 0xA045)\n");break;
	default: printf ("  type: *UNKNOWN*\n");break;
    }
    printf ("  fw  : v%4.2f\n", 1.0*mppt.fw/100);
    printf ("  ser : %s\n", mppt.ser);

    printf ("panel:\n");
    printf ("  vpv : %6.3fV\n", 1.0*mppt.vpv/1000);
    printf (" [ipv : %6.3fA]\n", 1.0*mppt.ppv/mppt.vpv*1000);
    printf ("  ppv : % 3dW\n", mppt.ppv);

    printf ("battery:\n");
    printf ("  v   : %6.3fV\n", 1.0*mppt.v/1000);
    printf ("  i   : %6.3fA\n", 1.0*mppt.i/1000);

    printf (" [p   : %6.3fW]\n", 1.0*mppt.v/1000*mppt.i/1000);

    printf ("load:\n");
    printf (" [v   : %6.3fV (same voltage as battery)]\n", 1.0*mppt.v/1000);
    if (mppt.fw >= 115) {
	printf ("  il  : %6.3fA\n", 1.0*mppt.il/1000);
	printf (" [pl  : %6.3fW\n]", 1.0*mppt.v/1000*mppt.il/1000);
    }
    else {
        printf ("  il  : --.--- (parameter only in fw >= v1.15)\n");
        printf (" [pl  : --.--- (calculated only if fw >= v1.15)]\n");
    }

    printf ("charger status:\n");
//    printf ("cs  : %d\n", mppt.cs);
    switch(mppt.cs) {
	case 0: printf ("  cs  : Off\n"); break;
	case 2: printf ("  cs  : Fault\n"); break;
	case 3: printf ("  cs  : Bulk\n"); break;
	case 4: printf ("  cs  : Absorption\n"); break;
	case 5: printf ("  cs  : Float\n"); break;
	default: printf ("  cs  : *UNKNOWN*\n"); break;
    }

//    printf ("err : %d\n", mppt.err);
    switch (mppt.err) {
	case 0: printf ("  err : No error\n");break;
	case 1: printf ("  err : Battery temperature too high\n");break;
	case 2: printf ("  err : Battery voltage too high\n");break;
	case 17: printf ("  err : Charger temperature too high\n");break;
	case 18: printf ("  err : Charger over current\n");break;
	case 19: printf ("  err : Charger current reversed\n");break;
	case 20: printf ("  err : Bulk time limit exceeded\n");break;
	case 21: printf ("  err : Current sensor issue\n");break;
	case 26: printf ("  err : Terminals overheated\n");break;
	case 33: printf ("  err : Input voltage too high (solar panel)\n");break;
	case 34: printf ("  err : Input current too high (solar panel)\n");break;
	case 38: printf ("  err : Input shutdown (due to excessive battery voltage)\n");break;
	case 116: printf ("  err : factory calibration data lost\n");break;
	case 117: printf ("  err : invalid/incompatible firmware\n");break;
	case 119: printf ("  err : User settings invalid\n");break;
	default: printf ("  err : *UNKNOWN\n");break;
    }

    if (mppt.fw >= 112) {
//        printf ("load: %d\n", mppt.load);
	switch(mppt.load) {
	    case 0: printf ("  load: Off\n");break;
	    case 1: printf ("  load: On\n");break;
	    default: printf ("  load: *UNKNOWN*\n");break;
	}
    }
    else {
        printf ("  il  : --- (parameter only in fw >= v1.12)\n");
    }

    printf ("  yield total         : %6.2fkWh\n", 1.0*mppt.yield_total/100);
    printf ("  yield today         : %6.2fkWh [%6.2fAh @ 13V nom.]\n", 1.0*mppt.yield_today/100, 1.0*mppt.yield_today/100*1000/13);
    printf ("  yield yesterday     : %6.2fkWh\n", 1.0*mppt.yield_yesterday/100);
    printf ("  max. power today    : % 4dW\n", mppt.maxpower_today);
    printf ("  max. power yesterday: % 4dW\n", mppt.maxpower_yesterday);

    if (mppt.fw >= 116) {
	printf ("  hsds: %d\n", mppt.hsds);
    }
    else {
        printf ("  hsds: --- (parameter only in fw >= v1.16)\n");
    }

    printf ("\n");
    printf ("Note: values in square brackets [] are calculated by this tool,\n      not in the charger.\n\n");
  }
  while (keepRunning && bCont);

    return 1;	// 0 - fail; 1 - success
}

void printHelp(void) {
	printf ("\n");
	printf ("%s %s %s\n", TOOLNAME, VERSION, COPYRIGHT);
	printf ("\n");
	printf ("options:\n");
	printf ("  -d dev : specify serial device to use\n");
	printf ("  -c : run continuously until Ctrl-C\n");
	printf ("  -h : print this help\n");
	printf ("\n");
}
