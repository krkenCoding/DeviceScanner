#!/bin/bash

trap ctrl_c INT

function ctrl_c() {
        echo " Program halted."
        rm -f formattedoutput.txt
        rm -f existingDevices.txt
        exit        
}

# If there are no arguments...
if [[ $# == 0 ]]; then
  cat misc/helpmenu.txt
  exit

# If there are arguments...
else
  # If first arguments are...
  # -h
  if [[ $1 == -h ]]; then
    cat misc/helpmenu.txt
    exit
    
  # -v
  elif [[ $1 == -v ]]; then
    python3 logs.py
    exit
  
  elif [[ $1 == -p ]]; then
    python3 pingIndividual.py $2
    exit


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
          
        # no third argument
        else echo "scan not saved anywhere."
        fi
      
      # Second argument is not rate, presume location
      else
        location=$2
      fi
    
    # if there is no second argument
    else 
      # UNCOMMENT WHEN READY TO SCAN sudo arp-scan -l
      echo "scan not saved anywhere!"
    fi 
    while true; do
      # if locations is not null
      if [[ -n $location ]]; then
        # echo "conducting scan..."
        sudo arp-scan -l > output.txt
        # if rate is not null
        if [[ -n $rate ]]; then
          echo "*" >> output.txt
        fi
        touch locations/$location.txt
        cp locations/$location.txt locations/$locations..txt
        python3 outputformat.py $location >> locations/$location.txt
        comm -13 --nocheck-order locations/$locations..txt locations/$location.txt
        rm locations/$locations..txt
        rm output.txt
        # echo "scan results saved at /locations/"$location".txt"
    
      # if location is null 
      else 
        sudo arp-scan -l > output.txt
        python3 outputformat.py $location > formattedoutput.txt
        if [[ -n $rate ]]; then
          echo * >> output.txt
        fi
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
  # second argument isn't recognized or there isn't one?
  else
    echo "there isn't a location or wrong arguments"
  fi
fi

