#!/usr/bin/python
import requests
from time import sleep
import json


IP='10.0.1.11'
secret='c9a9bbac33ceab3e9bd16125de638e42'

#http -j PUT http://10.0.1.11/api/c9a9bbac33ceab3e9bd16125de638e42/lights/2/state on:=true

on = json.dumps({'on': True})
off = json.dumps({'on': False})
lights = [1, 2, 3]

while 1:
    for light in lights:
        url = 'http://%s/api/%s/lights/%s/state' % (IP, secret, light)
        r = requests.put(url, data=on)
        sleep(1)
        r = requests.put(url, data=off)
        sleep(1)
