import re, datetime

f = open("output.txt", "r")
content = f.readlines()
f.close()

devicesFound = False
deviceCount = 0
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
