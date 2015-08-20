mpptdump
========
This tool reads out available data from Victron Energy BlueSolar charger (and others using VE.direct protocol)
and displays them in the shell. Output can be a single read-out or a continuous updating display of values. This is a command line tool.

* **MacOSX**: clone, make and enjoy.
* **Raspi** with FT232 USB-Serial Converter via ttyUSB0: clone, make and enjoy.
* **Raspi** with native serial interface ttyAMA0: For protecting your Raspi, place 2k2 series resistors into Tx and Rx lines, then clone, make and enjoy.
* **Linux**: not yet tried

mpptemoncms
===========
Similarly to mpptdump, this tool repeatedly reads out (and displays) data from VE.direct chargers,
and sends them to an emonCMS (http://emoncms.org/) host.

* **MacOSX**: clone, make, copy mpptemoncms.conf.default to mpptemoncms.conf and edit, and enjoy.
* **Raspi** with FT232 USB-Serial Converter via ttyUSB0: clone, make, copy mpptemoncms.conf.default to mpptemoncms.conf and edit, and enjoy.
* **Raspi** with native serial interface ttyAMA0: For protecting your Raspi, place 2k2 series resistors into Tx and Rx lines, then clone, make, copy mpptemoncms.conf.default to mpptemoncms.conf and edit, and enjoy.
* **Linux**: not yet tried

* Prerequisites: libconfig9, libconfig-dev
