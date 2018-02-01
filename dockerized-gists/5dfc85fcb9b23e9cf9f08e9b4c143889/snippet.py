#!/usr/bin/env python
# encoding: utf-8
"""
collect_meter.py

Created by Christian Stade-Schuldt on 2014-10-25.
"""

import sys
import os
import datetime
import serial
import time
import re
import sqlite3

# SML regexes 
complete_message_regex = '1b1b1b1b01010101.*1b1b1b1b.{8}'
meter_108_regex = '070100010800.{24}(.{8})0177'
meter_208_regex = '070100020800.{24}(.{8})0177'
meter_167_regex = '070100100700.{16}(.{8})0177'

def save_data_to_db(data):
    """saves the data tuple to the database"""
    con = sqlite3.connect("PATH_TO_SQLITE_FILE")

    con.isolation_level = None
    cur = con.cursor()

    query = '''INSERT INTO electricity_data VALUES (null, ?, ?, ?, ?)'''
    cur.execute(query, tuple([datetime.datetime.now().isoformat()] + data))

    con.commit()
    con.close()

def get_meter_data():
    ser = serial.Serial('/dev/ttyUSB0', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=0 )
    tty_error = 0
    t = 15
    if tty_error == 0:
        while t > 0:
            t -=1
            data = ser.read(2048)
            data = data.encode('hex')
            if re.match(complete_message_regex, data):
            
                m108 = re.search(meter_108_regex, data)
                m208 = re.search(meter_208_regex, data)
                m167 = re.search(meter_167_regex, data)
                
                if m108 and m208 and m167:
                    m167 = int(m167.group(1),16)
        		    # check if value is negative
                    if m167 > 0x7FFFFFFF:
        			m167 -= 0x100000000
                    m167 /= 10.0
                    m108 = int(m108.group(1),16)/10000.0
                    m208 = int(m208.group(1),16)/10000.0
                    return [m108, m208, m167]
            time.sleep(1)
        return None

def main():
    meter_data = get_meter_data()
    if meter_data:
	time.sleep(5)
        save_data_to_db(meter_data)

if __name__ == '__main__':
    main()
