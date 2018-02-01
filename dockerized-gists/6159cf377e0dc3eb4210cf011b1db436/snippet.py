#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import time
import logging
import sys
from parse import * # $ pip install pyparse
import serial # $ pip install pyserial

# Read and parse serial output from MightyOhm Geiger Counter v1.0
# http://mightyohm.com/blog/products/geiger-counter/
# by Roland Ortner (2015) https://github.com/dumboxp/geiger-counter
#    Tom Hensel <github@jitter.eu> 2016
# https://gist.github.com/gretel/6159cf377e0dc3eb4210cf011b1db436/

SERIAL_PORT = '/dev/cu.SLAB_USBtoUART'
LOG_FILE = './geiger-counter.log'
INTERVAL = 5

logger = logging.getLogger('geiger-counter')
hdlr = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

def run():
  logger.info("starting...");

  ser = serial.Serial(SERIAL_PORT, baudrate=9600, timeout=2, xonxoff=False, rtscts=False, dsrdtr=False)
  ser.flushInput()
  ser.flushOutput()

  while True:
    data_raw = ser.readline()
    try:
        data_raw = ser.readline(ser.in_waiting or 1)
        if data_raw:
            now = datetime.datetime.utcnow()
            #print(data_raw)
            array = parse("CPS, {}, CPM, {}, uSv/hr, {}, {}\r\n", data_raw)
            #print(array)
            cps = array[0].strip()
            cpm = array[1].strip()
            rad = array[2].strip()
            mod = array[3].strip()
            logger.info("%s; %s CPM, %s CPS, %s uSv, %s mode" % (now.strftime('%Y-%m-%d %H:%M:%S'), cpm, cps, rad, mod))
    except TypeError, Exception:
        logger.error("%s; exception on parsing data '%s'" % (now.strftime('%Y-%m-%d %H:%M:%S'), data_raw))
    except serial.SerialException:
        raise

    try:
        time.sleep(INTERVAL)
    except KeyboardInterrupt:
        logger.warn("interrupted by keyboard.");
        sys.exit(0)

run()

