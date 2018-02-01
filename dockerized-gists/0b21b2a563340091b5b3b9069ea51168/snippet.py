#!/usr/bin/env python2.7
# 802.11 probe requests processor
# Copyright (C) 2017 Ralon cybersecurity
# Loran Kloeze - loran@ralon.nl - @lorankloeze 
# MIT license: do with it what you want but use it for good
#
# Tested on OS X El Capitan 10.11.6 - MacBook Air
#
# This script grabs probe requests from the air and outputs them on the screen
# and/or saves them to a sqlite3-db. 
# On the screen it will simply prints a request as it comes in. If the database
# already contains a ssid/mac combination, it is overwritten.
#
# Reconnect your wifi if your network connection
# is lost after after using this script
#
# Prerequisites
#  - make sure 'tcpdump' is installed and in working order
#  - if tcpdump crashes, run this script again using sudo and doublecheck
#    your interface
#  
#
# It should output something like this when screen output is enabled
# 
#   Time     SSID                             Mac-address       Signal
#   11:23:44 GuestWIFI                        23:dd:89:12:3d:ff -89
#   11:24:01 GuestWIFI                        23:dd:89:12:3d:ff -87
#   11:23:44 ThomsonFF56D1                    67:d1:99:5a:bc:73 -76
#   .        .                                .                 .
#   .        .                                .                 .
#   .        .                                .                 .
 
import subprocess
import re
import sqlite3	
import time
import datetime
import os

### Settings

# The interface that is to be inspected. Make sure monitor mode is enabled for
# this interface.
monitor_dev = "en0"

# Enable output to stdout
output_to_stdout = True

# Enable save output to sqlite3-database
save_to_db = False

# Path of the sqlite3-database.
db_path = "/tmp/probes.db"

# Tcpdump may stop/crash if monitor_dev goes offline. Restart tcpdump in 
# restart_delay_sec seconds after it stops/crashes.
restart_delay_sec = 5 

### Program
mainConn = 0
mainCursor = 0

def prettyPrint(ant, mac, ssid):
    pad_spaces = 32 - len(ssid) # 32 is the max length of a 802.11 SSID
    while pad_spaces > 0:
        ssid += ' '
        pad_spaces -= 1
    
    niceTime = datetime.datetime.today().strftime('%H:%M:%S')
    print niceTime, ssid, mac, ant
    
def startProbing():    
    FNULL = open(os.devnull, 'w')
    proc = subprocess.Popen(['tcpdump','-l', '-I', '-i', monitor_dev, '-e', '-s', '256', 'type', 'mgt', 'subtype', 'probe-req'],
        stdout=subprocess.PIPE, stderr=FNULL)
        
    patt = "(-\\d+)dB signal .+SA:([0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+) .+Probe Request \\((.+)\\)"    
    while True:
        line = proc.stdout.readline()
        line = line.rstrip()
        if line != '':
            m = re.search(patt, line)
            if m is not None and len(m.groups()) == 3:
                ant = m.group(1).rstrip()                
                mac = m.group(2).rstrip()
                ssid = m.group(3).rstrip()
                timestamp = int(time.time())
                
                if output_to_stdout:
                    prettyPrint(ant, mac, ssid)
                if save_to_db:
                    mainCursor.execute("INSERT OR REPLACE INTO probes VALUES (?,?,?,?)", (ssid, mac, ant, timestamp))
                    mainConn.commit()
                    
        else:
            break      
def printIntro():
    print '+------------------------------------------------------------+'
    print '+ Scanner for enumerating probe requests from base stations  +'
    print '+                                                            +'
    print '+ (c) 2017 Ralon cybersecurity                               +'
    print '+ Loran Kloeze - loran@ralon.nl - @lorankloeze               +'
    print '+ License: MIT                                               +'
    print '+                                                            +'
    print '+------------------------------------------------------------+'
    print
    print 'Using monitor device', monitor_dev
    if save_to_db:
        print 'Saving requests to database at', db_path
    if output_to_stdout:
        print 'Pretty printing request is enabled'
        print 'It may take a while before the first requests appear'    
    print 'Start scanning...'
    print
    if output_to_stdout:
        print 'Time     SSID                             Mac-address       Signal'
    
    
def main():    
    if save_to_db: 
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
    
    while True:
        printIntro()
        startProbing()
        print "Tcpdump crashed/stopped, waiting for", restart_delay_sec, "seconds to restart"  
        time.sleep(restart_delay_sec)
    
    if save_to_db:        
        mainConn.close()

if __name__ == "__main__":
    main()