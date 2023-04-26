import sys, sqlite3, subprocess 

person = sys.argv[1]
conn = sqlite3.connect('LANScanner.db')
c = conn.cursor()
c.execute("SELECT * FROM devices WHERE Person=?",(person,))

results = c.fetchall()
if len(results) == 0:
    print("There's no one with that name in the database.")

for result in results:
    deviceIP = result[1]
    deviceMAC = result[2]
    command = ['nmap','-p','500',deviceIP]
    resultPortCheck = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output_lines = resultPortCheck.stdout.splitlines()
    if output_lines[1] == "Note: Host seems down. If it is really up, but blocking our ping probes, try -Pn":
        #host is down
        print("None of",person,"devices are currently connected.")
    else:
        # host is up
        print(result[6],"is connected")
	
conn.close()
