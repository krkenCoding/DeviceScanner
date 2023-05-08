import re, datetime, os, subprocess, sqlite3, sys


def getaninput():
    print("getting input.")
    test = input("#")


def portCheck(ip):
    port = '500'
    # Construct the Nmap command to scan the specified IP and port
    command = ['nmap', '-p', port, ip]
    # Use subprocess to execute the command and capture the output
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    # Print the output (for debugging purposes)
    output_lines = result.stdout.splitlines()
    if output_lines[1] == "Note: Host seems down. If it is really up, but blocking our ping probes, try -Pn":
        # HOST IS ACTUALLY DOWN
        return True
    else:
        # host is up
        return False
    # You can then use the 'result.stdout' variable to access the output of the command


def portScan(IPAddress, DeviceID):
    portScanOutput = os.system("nmap -F -Pn " + IPAddress + "> portscan.txt")
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

                c.execute("INSERT INTO ports (deviceID, Port, State, Service) VALUES (?, ?, ?, ?)",
                          (DeviceID, line[0], line[1], line[2],))
                conn.commit()
        except IndexError:
            pass


def currentTime():
    x = datetime.datetime.now()
    thePresent = x.strftime("%c").split()
    return thePresent


if __name__ == '__main__':
    # Opening the output file (the result of the arp scan)
    f = open("output.txt", "r")
    outputContent = f.readlines()
    f.close()

    existingDevices = []
    updatedDevices = []
    lastLine = outputContent[-1].replace("\n", "")

    # checking to see if existingDevices.txt exists. This means that multiple scans will be ran.
    if os.path.isfile("./existingDevices.txt"):
        # open that file
        f = open("existingDevices.txt", "r")
        content = f.readlines()
        f.close()

        # go through all the content
        for line in content:
            line = line.replace("\n", "")
            existingDevices.append(line)

        # open the output file
        f = open("output.txt", "r")
        content = f.readlines()
        f.close()
        for line in content:
            line = line.replace("\n", "")
            try:
                firstElement = line.split()[0]
            except IndexError:
                continue
            match = re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", firstElement)
            if bool(match) == True:
                if "(DUP:" in line.split():
                    continue
                else:
                    updatedDevices.append(line)

        newDevices = []
        f = open("existingDevices.txt", "a")
        for device in updatedDevices:
            if device not in existingDevices:
                existingDevices.append(device)
                newDevices.append(device)
        # print(".")
        if len(newDevices) > 0:
            thePresent = currentTime()
            conn = sqlite3.connect('LANScanner.db')
            c = conn.cursor()
            for device in newDevices:
                outputDevice = device.split()
                c.execute("SELECT * FROM devices WHERE IPAddress=? AND MACAddress=?",
                          (outputDevice[0], outputDevice[1],))
                result = c.fetchone()
                if result is None:
                    vendorFormatted = ' '.join(outputDevice[2:])
                    c.execute(
                        "INSERT INTO devices (IPAddress, MACAddress, Vendor, Location, isNew) VALUES (?, ?, ?, ?, ?)",
                        (outputDevice[0], outputDevice[1], vendorFormatted, sys.argv[1], 1,))
                    # NEED TO REPLACE RESULT[0] WITH THE DEVICEID
                    c.execute("SELECT * FROM devices WHERE IPAddress=? AND MACAddress =?",
                              (outputDevice[0], outputDevice[1],))
                    result = c.fetchone()
                    c.execute(
                        "INSERT INTO logbook (EventTime, Device, Activity, Location) VALUES (CURRENT_TIMESTAMP, ?, 'Connected', ? )",
                        (result[0], sys.argv[1]))
                    conn.commit()
                else:
                    continue
                conn.commit()

                #portScan(outputDevice[0], result[0])

                print(outputDevice[0], "has connected @", thePresent[3])
        legacyDevices = []
        for device in existingDevices:
            if device not in updatedDevices:
                existingDevices.remove(device)
                legacyDevices.append(device)
        if len(legacyDevices) > 0:
            disconnectedDevices = []
            for device in legacyDevices:
                outputDevice = device.split()
                if portCheck(outputDevice[0]):
                    disconnectedDevices.append(outputDevice[0])
                else:
                    existingDevices.append(device)
            if len(disconnectedDevices) > 0:
                conn = sqlite3.connect('LANScanner.db')
                c = conn.cursor()
                thePresent = currentTime()
                for device in disconnectedDevices:
                    print(device, "has disconnected @", thePresent[3])
                    c.execute("SELECT * FROM devices WHERE IPAddress=?", (
                        device,))  # WE NEED IT TO DO THE MAC ADDRESS TOO BECAUSE THE LIKIHOOD OF THERE BEING TWO OF THE SAME IP ADDRESSES ARE QUITE HIGH.
                    result = c.fetchone()
                    c.execute(
                        "INSERT INTO logbook (EventTime, Device, Activity, Location) VALUES (CURRENT_TIMESTAMP, ?, 'Disconnected', ? )",
                        (result[0], sys.argv[1]))
                    conn.commit()

        f.close()
        f = open("existingDevices.txt", "w")
        for line in existingDevices:
            f.write(line)
            f.write("\n")
        quit()



    # Checking if multiple scans will be ran, if so a file needs to be created
    elif lastLine == "*":
        # creates the file existingDevices.txt
        f = open("existingDevices.txt", "w")
        # go through all the lines of output
        for line in outputContent:
            # remove the \n that's in all lines
            line = line.replace("\n", "")
            # try splitting the lines into elements, we want the first element
            # some lines have no content hence the try
            try:
                firstElement = line.split()[0]
            except IndexError:
                continue
            # if the first element matches the ipv4 format then...
            match = re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", firstElement)
            if bool(match) == True:
                # be sure the device isn't a dup which is common
                if "(DUP:" in line.split():
                    continue
                else:
                    # if not a dupe then write the line into existingDevices.txt
                    f.write(line)
                    # newline
                    f.write("\n")
        f.close()

    devicesFound = False
    deviceCount = 0

    # Going through every line of the file
    for line in outputContent:
        line = line.replace("\n", "")
        try:
            firstElement = line.split()[0]
        except IndexError:
            continue
        # Seeing if the first element matches the IPv4 format...
        match = re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", firstElement)

        # ...If it does...
        if bool(match) == True:
            # ...Be sure to ignore duplicates...
            if "(DUP:" in line.split():
                continue
            else:
                # If this is the first device, then this will trigger causing the header to be printed
                if devicesFound == False:
                    conn = sqlite3.connect('LANScanner.db')
                    c = conn.cursor()
                    # Try to create the table if you run into errors then the table already exists
                    try:
                        # Create a table
                        c.execute('''CREATE TABLE devices
                                     (deviceID INTEGER PRIMARY KEY AUTOINCREMENT, IPAddress TEXT, MACAddress TEXT, Vendor TEXT, Person TEXT, DeviceType TEXT, Title TEXT, Location TEXT, isNew INTEGER)''')
                        c.execute('''CREATE TABLE logbook 
                                (EventTime DATETIME, Device INTEGER, Activity TEXT, Location TEXT)''')
                        # Save the changes
                        conn.commit()
                    except sqlite3.OperationalError:
                        pass

                    thePresent = currentTime()
                    print("\n", thePresent[3], "                                           ", thePresent[0],
                          thePresent[2],
                          thePresent[1], thePresent[4])
                    print("--Assignment--------- IP -------------- MAC ---------------- Vendor ----------------------")
                    devicesFound = True
                deviceCount += 1
                line = line.split()
                vendorFormatted = ' '.join(line[2:])
                c.execute("SELECT * FROM devices WHERE IPAddress=? AND MACAddress =?", [line[0], line[1]])
                result = c.fetchone()

                if result is None:
                    print("      -        ", line[0], "", line[1], "", vendorFormatted)
                else:
                    if result[6] is None:
                        print("      -        ", line[0], "", line[1], "", vendorFormatted)
                    else:
                        print(result[6], "", line[0], line[1], "", vendorFormatted)
                c.execute("SELECT * FROM devices WHERE IPAddress=? AND MACAddress =?", (line[0], line[1],))
                result = c.fetchone()
                if result is None:
                    c.execute(
                        "INSERT INTO devices (IPAddress, MACAddress, Vendor, Location, isNew) VALUES (?, ?, ?, ?, ?)",
                        (line[0], line[1], vendorFormatted, sys.argv[1], 1,))
                    conn.commit()

                    c.execute("SELECT * FROM devices WHERE IPAddress=? AND MACAddress =?", [line[0], line[1]])
                    result = c.fetchone()
                    # portScan(result[1], result[0])
                else:
                    continue
                c.execute("SELECT * FROM devices WHERE IPAddress=? AND MACAddress =?", [line[0], line[1]])
                result = c.fetchone()
                c.execute(
                    "INSERT INTO logbook (EventTime, Device, Activity, Location) VALUES (CURRENT_TIMESTAMP, ?, 'Connected', ? )",
                    (result[0], sys.argv[1]))
                conn.commit()

    print("\n" + str(deviceCount), "devices found.")
    print("------------------------------------------------------------------------------------------")
    try:
        conn.close()
    except NameError:
        pass
