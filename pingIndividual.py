import sys, sqlite3, subprocess 

# Fetch the person from the arguments
person = sys.argv[1]
# Connect to the database
conn = sqlite3.connect('LANScanner.db')
c = conn.cursor()
# Show only the devices that the person is associated to
c.execute("SELECT * FROM devices WHERE Person=?",(person,))
results = c.fetchall()
# If no results then the person isn't associated to any device
if len(results) == 0:
    print("There's no one with that name in the database.")
    exit()
# Else there are devices associated with the person searched for
else:
    personConnected = False
    # For each of the device that is associated with the person
    for result in results:
        # get the device's ip
        deviceIP = result[1]
        # get the device's mac
        deviceMAC = result[2]
        # construct the nmap port scan
        command = ['nmap','-p','500',deviceIP]
        # run the nmap port scan
        resultPortCheck = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        # split the output by the lines 
        output_lines = resultPortCheck.stdout.splitlines()
        # if this message is in the second line...
        if output_lines[1] == "Note: Host seems down. If it is really up, but blocking our ping probes, try -Pn":
            # ...this means the host is down
            pass
        # If the message didn't show up though...
        else:
            # ...this means that the host is up
            print(result[6],"is connected")
            # ...and so it's likely that the person is on the network
            personConnected = True
    # Close the connection to the network
    conn.close()
    # If the boolean remained false then no connection could be established to any of the devices 
    if personConnected == False:
         print("None of",person,"devices are currently connected.")
