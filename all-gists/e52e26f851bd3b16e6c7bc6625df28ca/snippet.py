#!/usr/bin/python

import serial
import sqlite3 as lite
import sys
import time

while True:
    ser = serial.Serial(
        port='/dev/ttyUSB0',\
        baudrate=9600,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
            timeout=0)
    
    #print("connected to: " + ser.portstr)

    #this will store the line
    line = ""
    while True:
        for c in ser.read():
            line = line+c
            if c == '\n':
    #           print(line)
                break
        if len(line) > 0:
            if line[-1] == '\n':
                if line.startswith("|S"):
                    break
                else:
                    line=""
    results = line.split("|")
    source = ""
    voltage = ""
    
    try:
        con = lite.connect('/srv/pdu/pdu.sql')
    
        with con:
            cur = con.cursor() 
            for result in results:
             if (result != "") and (result != '\r\n'):
               if result[0] == "B":
                 print("Battery: "+result.split(":")[1]+"V")
                 source = "Battery"
               if result[0] == "S":
                 print("Solar: "+result.split(":")[1]+"V")
                 source = "Solar"
               if result[0] == "R":
                 print("Regulator: "+result.split(":")[1]+"V")
                 source = "Regulator"
               if result[0] == "W":
                 print("Power: "+result.split(":")[1]+"mW")
                 source = "Power"
               voltage = result.split(":")[1]
               cur.execute('INSERT INTO voltages (source,value) VALUES (?,?)',(source,voltage))
               con.commit()
            ser.close()
    except lite.Error, e:
        
        if con:
            con.rollback()
            
        print "Error %s:" % e.args[0]
        sys.exit(1)
        
    finally:
        
        if con:
            con.close()
    time.sleep(30