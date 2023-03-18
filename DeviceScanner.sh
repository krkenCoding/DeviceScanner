#!/bin/bash

trap ctrl_c INT

function ctrl_c() {
        echo " Program halted."
        rm -f formattedoutput.txt
        exit        
}

# If there are no arguments...
if [[ $# == 0 ]]; then
  echo "help menu tba"

# If there are arguments...
else
  # If first arguments are...
  # -h
  if [[ $1 == -h ]]; then
    cat misc/helpmenu.txt
    exit
    
  # -v
  elif [[ $1 == -v ]]; then
    echo "view logs tba"
 
  # if there is a scan argument
  elif [[ $1 == -s ]]; then
  
    # if the second argument is not null
    if [[ -n $2 ]]; then
    
      # if the second argument is the rate
      if [[ $2 == *"-r"* ]]; then
        if [[ $2 == "-r1" ]]; then
          rate=600 # 10 mins
        elif [[ $2 == "-r2" ]]; then
          rate=300
        elif [[ $2 == "-r3" ]]; then
          rate=60
        elif [[ $2 == "-r4" ]]; then
          rate=1
        else 
          echo "rate not set, please input a number between 1 and 4 after -r"
          exit
        fi
        
        # if there is a third argument (presume location)
        if [[ -n $3 ]]; then
          location=$3
          echo "location scanned:" $location
          
        # no third argument
        else echo "scan not saved anywhere."
        fi
      
      # Second argument is not rate, presume location
      else
        location=$2
        echo "location scanned:" $location
      fi
    
    # if there is no second argument
    else 
      # UNCOMMENT WHEN READY TO SCAN sudo arp-scan -l
      echo "scan not saved anywhere!"
    fi 
    
  # second argument isn't recognized or there isn't one?
  else
    echo "there isn't a location or wrong arguments"
  fi
fi
while true; do
  # if locations is not null
  if [[ -n $location ]]; then
    echo "conducting scan..."
    sudo arp-scan -l > output.txt
    python3 outputformat.py output.txt >> locations/$location.txt
    cat locations/$location.txt
    rm output.txt
    echo "scan results saved at /locations/"$location".txt"

  # if location is null 
  else 
    sudo arp-scan -l > output.txt
    python3 outputformat.py output.txt > formattedoutput.txt
    rm output.txt
    cat formattedoutput.txt
    echo "Would you like to save this scan in a location? (y/N)"
    read toSave
    if [[ $toSave == "y" ]]; then
      echo "Where is the location?"
      read saveLocation
      cat formattedoutput.txt >> locations/$saveLocation.txt
    elif [[ $toSave == "n" ]]; then
      rm formattedoutput.txt
      exit
    else
      rm formattedoutput.txt
      exit
    fi
  fi
  # If there is no rate then exit the program
  if [[ -z $rate ]]; then
    exit
  # else wait however long before scanning again
  else
    sleep $rate
  fi
done
