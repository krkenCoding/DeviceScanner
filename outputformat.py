import re, datetime, os

# Opening the output file (the result of the arp scan)
f = open("output.txt", "r")
content = f.readlines()
f.close()

existingDevices = []
updatedDevices = []

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

    # open the second output
    f = open("output2.txt", "r")
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

    print()
    print("Devices that have since connected:")
    f = open("existingDevices.txt", "a")
    for device in updatedDevices:
        if device not in existingDevices:
            print(device)
            existingDevices.append(device)

    print()
    print("Devices that have since disconnected:")
    for device in existingDevices:
        if device not in updatedDevices:
            existingDevices.remove(device)
            print(device)
    f.close()
    f = open("existingDevices.txt", "w")
    for line in existingDevices:
        f.write(line)
        f.write("\n")
    quit()

lastLine = content[-1].replace("\n", "")

# Checking if multiple scans will be ran, if so a file needs to be created
if lastLine == "*":
    f = open("existingDevices.txt", "w")
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
                f.write(line)
                f.write("\n")
    f.close()

devicesFound = False
deviceCount = 0

# Going through every line of the file
for line in content:
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
                x = datetime.datetime.now()
                thePresent = x.strftime("%c").split()
                print(thePresent[3],"                                           ",thePresent[0], thePresent[2], thePresent[1], thePresent[4])
                print("---- IP -------------- MAC ---------------- Vendor -----------------")
                devicesFound = True
            deviceCount += 1
            print(line)

print("\n"+str(deviceCount), "devices found.")
print("--------------------------------------------------------------------")
