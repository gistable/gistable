#!/usr/bin/env python
from collections import deque
import Queue
import csv
import datetime
import os
import re
import subprocess
import multiprocessing as mp

# devicelist.csv = HOSTNAME,IP

def loadDevices():
    with open('devicelist.csv', 'rb') as csvfile:
        devices = csv.reader(csvfile, delimiter=',', quotechar='"')
        dev = [(dev,ip) for dev,ip in devices]
    return dev

def loadIPs():
    loadDevices()
    IPs = [i[1] for i in loadDevices()]
    print IPs
    return IPs

def testIP(IP):
    """ test an IP address to see if it's up with one ping"""
    """ will feed this an array with mp.Pool.map() """
    IPup = []
    IPdown = []
    with open(os.devnull, "w") as fnull:
        if subprocess.call(['ping','-c 1 -W 1',IP,],stdout=fnull, stderr=fnull)==0:
            print 'host %s is UP' % IP
            return IP
        else:
            print 'host %s is DOWN' % IP
            return None

numThreads = 20
IPs = loadIPs()
print IPs
p = mp.Pool(numThreads)
""" IPout is a list of the devices that are UP """
IPout = p.map(testIP,IPs)
print IPout
p.close()
p.join()
