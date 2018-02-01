#!/usr/bin/env python2.7
# 802.11 probe requests processor
# Copyright (C) 2017 Ralon cybersecurity
# Loran Kloeze - loran@ralon.nl - @lorankloeze 
# MIT license: do with it what you want but use it for good
#
# This script grabs probe requests from the air and puts them in a sqlite3-db. 
# It cleans up the database to prevent old entries from filling up too much disk
# space. Check the regex before starting this script because it assumes 3
# antennas on the wireless device.
#
#

import subprocess
import re
import sqlite3	
import time
import threading

### Settings

# The interface that is to be inspected. Make sure monitor mode is enabled for
# this interface.
monitor_dev = "wlan1"

# Path of the sqlite3-database.
db_path = "/html/db/probes.db"

# Tcpdump may stop/crash if monitor_dev goes offline. Restart tcpdump in 
# restart_delay_sec seconds after it stops/crashes.
restart_delay_sec = 5 

# Purge the database every purge_db_sec seconds.
purge_db_sec = 1 * 60

# Purge entries old than max_age_sec seconds from the database.
max_age_sec = 3 * 60


### Program
mainConn = 0
mainCursor = 0

# Thread to purge the database. Entries older than max_age_sec are removed.
class CleanDBThread(threading.Thread):
     def __init__(self):
         super(CleanDBThread, self).__init__()

     def run(self):
         while True:
             remove_before_ts = int(time.time()) - max_age_sec
             print "Removing probes older than", remove_before_ts
             cleanConn = sqlite3.connect(db_path, 60)
             cClean = cleanConn.cursor()
             cClean.execute("DELETE FROM probes WHERE last_seen < ?", [remove_before_ts])
             cleanConn.commit()
             cleanConn.close()
             time.sleep(purge_db_sec)

def startProbing():    
    # If you want to copy/paste: tcpdump -l -I -i wlan1 -e -s 256 type mgt subtype probe-req
    proc = subprocess.Popen(['tcpdump', '-l', '-I', '-i', monitor_dev, '-e', '-s', '256', 'type', 'mgt', 'subtype', 'probe-req'],stdout=subprocess.PIPE)
    patt = '(-\d+)dBm signal antenna 0 (-\d+)dBm signal antenna 1 (-\d+)dBm signal antenna 2.+SA:([0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+) .+(Probe Request) \((.+)\)'
    while True:
        line = proc.stdout.readline()
        if line != '':
            m = re.search(patt, line)
            if m is not None and len(m.groups()) == 6:
                ant0 = m.group(1).rstrip()
                ant1 = m.group(2).rstrip()
                ant2 = m.group(3).rstrip()
                
                # Calculate average of three antennas
                ant_avg = (int(ant0)+int(ant1)+int(ant2))/3 
                
                mac = m.group(4).rstrip()
                ssid = m.group(6).rstrip()
                timestamp = int(time.time())
                mainCursor.execute("INSERT OR REPLACE INTO probes VALUES (?,?,?,?)", (ssid, mac, ant_avg, timestamp))
                mainConn.commit()
        else:
            break      

def main(): 
    global mainConn
    global mainCursor
    
    mainConn = sqlite3.connect(db_path)
    mainCursor = mainConn.cursor()
    mainCursor.execute('''CREATE TABLE IF NOT EXISTS probes
                 (ssid text, mac text, ant numeric, last_seen numeric)''')
    mainCursor.execute('''CREATE UNIQUE INDEX IF NOT EXISTS ssid_index ON probes
                 (ssid)''')       
    mainCursor.execute('''CREATE INDEX IF NOT EXISTS last_seen_index ON probes
                 (last_seen)''')                   
    mainConn.commit()
    
    purgeThread = CleanDBThread()
    purgeThread.daemon = True
    purgeThread.start()
    
    while True:      
        print "Starting probe search on", monitor_dev, "saving to", db_path
        startProbing()
        print "Probe search stopped, waiting for", restart_delay_sec, "seconds to restart"  
        time.sleep(restart_delay_sec)
        
    mainConn.close()

if __name__ == "__main__":
    main()
