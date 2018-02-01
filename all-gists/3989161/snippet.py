#!/usr/bin/python

import mosquitto
import textwrap

def on_message(mosq, obj, msg):
    for s in textwrap.wrap(msg.payload, width=32):
        print(s)

mqttc = mosquitto.Mosquitto()
mqttc.on_message = on_message

mqttc.connect("test.mosquitto.org", 1883, 60)
mqttc.subscribe("#", 0)

rc = 0
while rc == 0:
    rc = mqttc.loop()
