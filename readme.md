Usage: ./DeviceScan.sh [options] [location]

You will need to be root, or arp-scan must be SUID root, in order to run
arp-scan, because the functions that it uses to read and write packets
require root privilege.


Options:
Note: where an option takes a value, that value is specified as a letter in
angle brackets. The letter indicates the type of data that is expected:

<i> An integer, which can be specified as a decimal number


--help or -h            Display this usage message and exit.

--scan or -s		Conduct the scan on your local network.

--rate<i> or -r<i>	Specify the rate in which the scan will be done...
	-r1		...slowest; every 10 minutes
	-r2		...every 5 minutes
	-r3		...every minute
	-r4		...fastest; conduct a scan everytime a scan is done. 
	
--view or -v		View already existing logs.

Example: ./DeviceScan.sh -s -r3 library
