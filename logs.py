import os, sqlite3, re

# Define the directory path
directory_path = './locations'

# Get a list of all files in the directory
file_list = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

print("Select which location log to view.")

locations=[]
num = 1
# Print the list of files
for location in file_list:
    location = location.replace(".txt","")
    locations.append(location)
    print(str(num)+".)", location)
    num+=1

locationChoice = int(input("\n#:"))
locationTitle = locations[locationChoice-1]
print(locationTitle,"selected.\n")

f = open("locations/"+locationTitle+".txt","r")
content = f.readlines()

devices = []
for line in content:
    line=line.replace("\n","")
    print(line)
    try:
            firstElement = line.split()[0]
    except IndexError:
        continue
    # if the first element matches the ipv4 format then...
    match = re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", firstElement)
    if match:
        devices.append(firstElement)


newDevicesAmount = 0
conn = sqlite3.connect('LANScanner.db')
c = conn.cursor()
for device in devices:
    c.execute("SELECT * FROM devices WHERE IPAddress=?", (device,)) #AND MACAddress=?", (firstElement,)) #ADD MAC ADDRESSES TO THIS.
    result = c.fetchone()
    if result[7] == 1:
        newDevicesAmount +=1

if newDevicesAmount>0:
    print("\nThere are", newDevicesAmount, "new devices in this log.")
    print("Would you like identify them? (y/N)") 

'''
c.execute("SELECT * FROM devices WHERE IPAddress=? AND MACAddress=?", (outputDevice[0], outputDevice[1],))
rows = c.fetchall()


result = c.fetchone()

for row in rows:
    print(row)
    
conn.close()
'''

