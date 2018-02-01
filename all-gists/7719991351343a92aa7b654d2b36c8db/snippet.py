#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Sends HAL signals to the given MQTT broker host.
#
# usage: hal2mqtt.py [hostname]
#
# Video demo at https://www.youtube.com/watch?v=uFbr7xBjItE
#
# sudo apt-get install mosquitto mosquitto-clients python-mosquitto
# sudo pip install paho-mqtt

import sys
import re
import time
import hal
import logging

from machinekit import hal
import paho.mqtt.client as mqtt

import subprocess
from shlex import split

thread_sleep = 0 # sleep [sec] between updates
#thread_sleep = 0.001 # sleep [sec] between updates

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
#logging.basicConfig(stream=sys.stderr, level=logging.INFO)

v = {}

def hal2mqtt(client, name, value, t):

  d = ""

  if name in v:
    d = v[name]
    # print(d)

  if value != d:
    v[name] = value
    cmd = "%f %f" % (t, value)
    #print(cmd)
#    client.publish(name, cmd, 0, True) # qos0, retain
    client.publish(name, cmd, 0, False) # qos0, no retain
#    client.publish(name, cmd, 2, True)

def on_connect(client, userdata, rc):
#  client.subscribe("esp-01/gp2")
  return

def on_message(client, userdata, msg):
  return

class C :
  def __init__(self) :
    logging.debug("ready")
        
  def run(self) :
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    #client.username_pw_set(userID, password)

    host = sys.argv[1]
    client.connect(host, 1883, 60)

#    client.connect("test.mosquitto.org", 1883, 60)
#    client.connect("iot.eclipse.org", 1883, 60)
#    client.connect("localhost", 1883, 60)
    while 1:
      try:
        t = time.time()
        for sig in hal.signals():
          s = hal.Signal(sig)
          for pin in s.pins():
            if (pin.name == "pwmgen.0.pwm"): # filter by name
              hal2mqtt(client, pin.name, float(pin.get()), t)
                               
          time.sleep(thread_sleep)
      except KeyboardInterrupt :
        raise SystemExit

i = C()
i.run()
