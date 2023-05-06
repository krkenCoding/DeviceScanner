import os, sqlite3, re, time


def clearandwait():
    # Wait for a fraction of a second
    time.sleep(0.25)
    # Clear the terminal's screen
    os.system("clear")

def portScan(IPAddress, DeviceID):
    # Conduct a port scan on the top 1000 ports and save it in a text file
    portScanOutput = os.system("nmap -F -Pn " + IPAddress + "> portscan.txt")
    # Open the text file
    f = open("portscan.txt", "r")
    # save all the contents into a variable
    content = f.readlines()
    # 
    firstPort = True
    for line in content:
        line = line.replace("\n", "")
        try:
            if line[0].isdigit():
                if firstPort is True:
                    line = line.split()
                    conn = sqlite3.connect('LANScanner.db')
                    c = conn.cursor()
                    try:
                        # Try creating a port table  
                        c.execute('''CREATE TABLE ports
                                (deviceID INTEGER, Port INTEGER, State TEXT, Service TEXT)''')
                        conn.commit()
                    except sqlite3.OperationalError:
                        # if it already exists, never mind
                        pass
                # Insert into this port table the device id, ports, the states, and what the service is
                c.execute("INSERT INTO ports (deviceID, Port, State, Service) VALUES (?, ?, ?, ?)",
                          (DeviceID, line[0], line[1], line[2],))
                # commit to this table
                conn.commit()
        except IndexError:
            pass

def viewingDevice(result, ask):
    clearandwait()
    conn = sqlite3.connect('LANScanner.db')
    c = conn.cursor()
    print("--Assignment--------- IP -------------- MAC ---------------- Vendor ----------------------")
    if result[6] is None:
        print("      -        ", result[1], "", result[2], "", result[3])
    else:
        print(result[6], "", result[1], "", result[2], "", result[3])
    print("------------------------------------------------------------------------------------------")
    print("\nPort Info:")
    try:
        c.execute("SELECT * FROM ports WHERE deviceID=?", (result[0],))
        ports = c.fetchall()
        print("---- Port -------------- State ---------------- Service -----------------")
        if len(ports) == 0:
            print("		No open/filtered ports were detected")
        else:
            for line in ports:
                print("   ",line[1], "          ",line[2], "               ", line[3])
        print("-------------------------------------------------------------------------")
    except sqlite3.OperationalError:
        print("Port scan not ran yet")

    c.execute("SELECT * FROM logbook WHERE Device=?", (result[0],))
    activity = c.fetchall()
    if activity is None:
        print("No logs to show!")
    else:
        print("\nLogs:")
        print("---- Location -------------- Activity ---------------- Time -----------------")
        for log in activity:
            # log=log.split()
            print("   ", log[3], "         ", log[2], "         ", log[0])

        print("-----------------------------------------------------------------------------")

    if ask == True:
        print("Who would you like to assign this device to?")
        nameInput = input(">")
        c.execute('UPDATE devices SET Person = ? WHERE deviceID = ?', (nameInput, result[0],))
        conn.commit()
        print("What type of device is this?")
        typeInput = input(">")
        c.execute('UPDATE devices SET DeviceType = ? WHERE deviceID = ?', (typeInput, result[0],))
        conn.commit()
        suggestedLabel = nameInput + " " + typeInput
        print("Are you happy with the label: '" + suggestedLabel + "' ? (y/N)")
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
        print("Would you like to...\n1.) Edit \n2.) Run a port scan \n3.) Delete the device \n4.) Go back...")
        userInput = int(input(">"))
        if userInput == 2:
            print("loading...")
            portScanOutput = os.system("nmap -sV -Pn -T5 " + result[1] + " > portscan.txt")

            f = open("portscan.txt", "r")
            content = f.readlines()
            firstPort = True
            for line in content:
                line = line.replace("\n", "")
                try:
                    if line[0].isdigit():
                        if firstPort is True:
                            line = line.split()
                            conn = sqlite3.connect('LANScanner.db')
                            c = conn.cursor()
                            try:
                                c.execute('''CREATE TABLE ports
                                        (deviceID INTEGER, Port INTEGER, State TEXT, Service TEXT)''')
                                conn.commit()
                            except sqlite3.OperationalError:
                                pass
                        c.execute("SELECT * FROM ports WHERE deviceID=? AND Port=?",(result[0],line[0],))
                        searchPort = c.fetchall()
                        if len(searchPort)==0:
                            c.execute("INSERT INTO ports (deviceID, Port, State, Service) VALUES (?, ?, ?, ?)",
                                  (result[0], line[0], line[1], line[2],))
                            conn.commit()
                except IndexError:
                    pass

            viewingDevice(result, False)

        if userInput == 4:
            viewingLocation(result[7])


def viewingLocation(locationTitle):
    clearandwait()
    print("Viewing", locationTitle, "logs.\n")

    f = open("locations/" + locationTitle + ".txt", "r")
    content = f.readlines()

    devices = []
    for line in content:
        line = line.replace("\n", "")
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
    file_list = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f)) and f!="..txt"]

    print("Select which location log to view. (Or enter a non-int to close)")

    locations = []
    num = 1
    # Print the list of files
    for location in file_list:
        location = location.replace(".txt", "")
        locations.append(location)
        print(str(num) + ".)", location)
        num += 1

    try:
        locationChoice = int(input("\n#:"))
        locationTitle = locations[locationChoice - 1]
    except ValueError:
        print("Quitting!")
        time.sleep(0.25)
        exit()

    clearandwait()
    viewingLocation(locationTitle)


def newDeviceCheck(devices):
    newDevicesID = []
    for device in devices:
        c.execute("SELECT * FROM devices WHERE IPAddress=?",
                  (device,))  # AND MACAddress=?", (firstElement,)) #ADD MAC ADDRESSES TO THIS
        result = c.fetchone()
        if result[8] == 1:
            newDevicesID.append(result[0])

    num = 1
    if len(newDevicesID) > 0:
        print("\nThere are", len(newDevicesID), "new devices in this log.")
        print("Would you like to identify any of them? (y/N)")
        userChoice = input(">")
        if userChoice == "y":
            print("\nPick a device to identify:")
            for device in newDevicesID:
                c.execute('SELECT * from devices WHERE deviceID=?', (device,))
                result = c.fetchone()
                print(str(num) + ".)", result[1])
                num += 1
            deviceChoice = int(input("#"))
            c.execute("SELECT * FROM devices WHERE deviceID=?", (newDevicesID[deviceChoice - 1],))
            result = c.fetchone()
            clearandwait()
            viewingDevice(result, True)


        elif userChoice == "n" or userChoice == "N":
            print("\nSelect a device or go back by entering anything else.")

            for i, device in enumerate(devices):
                print(str(i + 1) + ".)", device)
            try:
                deviceChoice = int(input("#"))
                print(devices[deviceChoice - 1], "selected")
                c.execute("SELECT * FROM devices WHERE IPAddress=?", (devices[deviceChoice - 1],))
                result = c.fetchone()
                viewingDevice(result, False)
            except ValueError:
                print("Going back...")
                clearandwait()
                locationSelect()

# Connect to the database
conn = sqlite3.connect('LANScanner.db')
c = conn.cursor()

while True:
    # The program begins with a location select
    locationSelect()

