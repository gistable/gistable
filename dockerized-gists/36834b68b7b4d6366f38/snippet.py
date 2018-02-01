#!/usr/bin/env python

import sqlite3
import threading
from time import time, sleep, gmtime, strftime

import serial
import requests

# global variales

# sqlite database location
dbname = 'templog.db'

# serial device
DEVICE = '/dev/ttyAMA0'
BAUD = 9600

ser = serial.Serial(DEVICE, BAUD)

# timeout in seconds for waiting to read temperature from sensors
TIMEOUT = 30

# weather underground data
WUKEY = ''
STATION = ''
# time between weather underground samples in seconds
SAMPLE = 30 * 60


def log_temperature(temp):
    """
    Store the temperature in the database.
    """
    
    conn = sqlite3.connect(dbname)
    curs = conn.cursor()

    curs.execute("INSERT INTO temps values(datetime('now', 'localtime'), '{0}', '{1}' )".format(temp['temperature'], temp['id']))

    conn.commit()
    conn.close()

    
def get_temp():
    """
    Retrieves the temperature from the sensor.

    Returns -100 on error, or the temperature as a float.
    """

    global ser

    tempvalue = -100
    deviceid = '??'
    voltage = 0

    fim = time() + TIMEOUT

    while (time() < fim) and (tempvalue == -100):
        n = ser.inWaiting()
        if n != 0:
            data = ser.read(n)
            nb_msg = len(data) / 12
            for i in range(0, nb_msg):
                msg = data[i*12:(i+1)*12]
                deviceid = msg[1:3]

                if msg[3:7] == "TMPA":
                    tempvalue = msg[7:]

                if msg[3:7] == "BATT":
                    voltage = msg[7:11]
                    if voltage == "LOW":
                        voltage = 0
        else:
            sleep(5)

    return {'temperature':tempvalue, 'id':deviceid}


def get_temp_wu():
    """
    Retrieves temperature(s) from weather underground (wu) and stores it to the database
    """

    try:
        conn = sqlite3.connect(dbname)
        curs = conn.cursor()
        query = "SELECT baudrate, port, id, active FROM sensors WHERE id like 'W_'"

        curs.execute(query)
        rows = curs.fetchall()

        #print(rows)

        conn.close()

        if rows != None:
            for row in rows[:]:
                WUKEY = row[1]
                STATION = row[0]

                if int(row[3]) > 0:
                    try:
                        url = "http://api.wunderground.com/api/{0}/conditions/q/{1}.json".format(WUKEY, STATION)
                        r = requests.get(url)
                        data = r.json()
                        log_temperature({'temperature': data['current_observation']['temp_c'], 'id': row[2]})
                    except Exception as e:
                        raise
                        
    except Exception as e:
        text_file = open("debug.txt", "a+")
        text_file.write("{0} ERROR:\n{1}\n".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()), str(e)))
        text_file.close()

         
def main():
    """
    Program starts here.
    """
    
    get_temp_wu()
    t = threading.Timer(SAMPLE, get_temp_wu)
    t.start()

    while True:
        temperature = get_temp()

        if temperature['temperature'] != -100:
            log_temperature(temperature)

        if t.is_alive() == False:
            t = threading.Timer(SAMPLE, get_temp_wu)
            t.start()

if __name__ == "__main__":
    main()
