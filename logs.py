import os, sqlite3, re, time

def clearandwait():
	time.sleep(0.25)
	os.system("clear")
	

def viewingDevice(result, ask):
	clearandwait()
	print("--Assignment--------- IP -------------- MAC ---------------- Vendor ----------------------")
	if result[6] is None:
		print("      -        ", result[1], "", result[2], "", result[3])
	else:
		print(result[6], "", result[1], "", result[2], "", result[3])		
		
	print("------------------------------------------------------------------------------------------")
	print("\nPort Info:")
	print("---- Port -------------- State ---------------- Service -----------------")
	print("                           TO BE ADDED")
	print("------------------------------------------------------------------------------------------")
	
	c.execute("SELECT * FROM logbook WHERE Device=?", (result[0],))
	activity = c.fetchall()
	if activity is None:
		print("No logs to show!")
	else:
		print("\nLogs:")
		print("---- Location -------------- Activity ---------------- Time -----------------")
		for log in activity:
			#log=log.split()
			print("      ",log[3], "               ", log[2], "         ", log[0])
			
		print("------------------------------------------------------------------------------------------")
    	
	if ask==True:
		print("Who would you like to assign this device to?")
		nameInput = input(">")
		c.execute('UPDATE devices SET Person = ? WHERE deviceID = ?', (nameInput, result[0],))
		conn.commit()
		print("What type of device is this?")
		typeInput = input(">")
		c.execute('UPDATE devices SET DeviceType = ? WHERE deviceID = ?', (typeInput, result[0],))
		conn.commit()
		suggestedLabel = nameInput + " " + typeInput
		print("Are you happy with the label: '" + suggestedLabel+"' ? (y/N)")
		userHappy = input(">")
		if userHappy:
			c.execute('UPDATE devices SET Title = ? WHERE deviceID = ?', (suggestedLabel, result[0],))
			conn.commit()
		else:
			titleInput = input(">")
			c.execute('UPDATE devices SET Title = ? WHERE deviceID = ?', (titleInput, result[0],))
			conn.commit()
		c.execute('UPDATE devices SET isNew = ? WHERE deviceID = ?', (0, result[0],))
		conn.commit()
		
		c.execute("SELECT * FROM devices WHERE deviceID=?", (result[0],))
		result = c.fetchone()
		viewingDevice(result, False)
	if ask == False:
		print("Would you like to...\n1.) Edit \n2.) Delete \n3.) Go back...")
		userInput = int(input("tba>"))
		if userInput == 3:
			viewingLocation(result[7])

def viewingLocation(locationTitle):
	clearandwait()
	print("Viewing",locationTitle,"logs.\n")


	f = open("locations/"+locationTitle+".txt","r")
	content = f.readlines()

	devices = []
	for line in content:
	    line=line.replace("\n","")
	    print(line)
	    try:
	    	firstElement = line.split()[0]
	    	secondElement = line.split()[1]
	    except IndexError:
	    	continue
	    # if the first element matches the ipv4 format then...
	    match = re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", firstElement)
	    match2 = re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", secondElement)
	    if match and firstElement not in devices:
	    	devices.append(firstElement)
	    elif match2 and secondElement not in devices:	
	    	devices.append(secondElement)
	newDeviceCheck(devices)


def locationSelect():
	# Define the directory path
	directory_path = './locations'

	# Get a list of all files in the directory
	file_list = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

	print("Select which location log to view. (Or enter a non-int to close)")

	locations=[]
	num = 1
	# Print the list of files
	for location in file_list:
	    location = location.replace(".txt","")
	    locations.append(location)
	    print(str(num)+".)", location)
	    num+=1

	try:
		locationChoice = int(input("\n#:"))
		locationTitle = locations[locationChoice-1]
	except ValueError:
		print("Quitting!")
		time.sleep(0.25)
		exit()
	
	
	clearandwait()
	viewingLocation(locationTitle)
		
def newDeviceCheck(devices):
	newDevicesID = []
	for device in devices:
		c.execute("SELECT * FROM devices WHERE IPAddress=?", (device,)) #AND MACAddress=?", (firstElement,)) #ADD MAC ADDRESSES TO THIS
		result = c.fetchone()		
		if result[8] == 1:
	    		newDevicesID.append(result[0])
		
	num = 1
	if len(newDevicesID)>0:
	    print("\nThere are", len(newDevicesID), "new devices in this log.")
	    print("Would you like to identify any of them? (y/N)")
	    userChoice = input(">")
	    if userChoice == "y":
	    	print("\nPick a device to identify:")
	    	for device in newDevicesID:
	    		c.execute('SELECT * from devices WHERE deviceID=?', (device,))
	    		result = c.fetchone()
	    		print(str(num)+".)",result[1])
	    		num+=1
	    	deviceChoice = int(input("#"))
	    	c.execute("SELECT * FROM devices WHERE deviceID=?", (newDevicesID[deviceChoice-1],))
	    	result = c.fetchone()
	    	clearandwait()
	    	viewingDevice(result, True)		
	    			
	    			
	    elif userChoice =="n" or userChoice == "N":
	    	print("\nSelect a device or go back by entering anything else.")
	    	
	    	for i, device in enumerate(devices):
	    			print(str(i+1)+".)", device)
	    	try:
	    		deviceChoice = int(input("#"))
	    		print(devices[deviceChoice-1],"selected")
	    		c.execute("SELECT * FROM devices WHERE IPAddress=?", (devices[deviceChoice-1],))
	    		result = c.fetchone()
	    		viewingDevice(result, False)
	    	except ValueError:
	    		print("Going back...")
	    		clearandwait()
	    		locationSelect()
	
conn = sqlite3.connect('LANScanner.db')
c = conn.cursor()

while True:
	locationSelect()
