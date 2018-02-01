#!/usr/bin/env python
# read CC2650 SensorTag by JP Mens
# follow https://smidgeonpigeon.wordpress.com/2015/07/21/raspberry-pi-2-ble-ti-sensor-tag/
# to get started, but use Sensortag2650.py

import time
import json
import struct
import Sensortag2650 as sensortag
import paho.mqtt.publish as mqtt

# don't even bother starting until you see your SensorTag
# $ hcitool -i hci1 lescan
# LE Scan ...
# B0:B4:48:BD:B8:05 CC2650 SensorTag

my_sensor = 'B0:B4:48:BD:B8:05'
tag = sensortag.SensorTag(my_sensor)

print "Connected to SensorTag", my_sensor

sensorOn  = struct.pack("B", 0x01)
sensorbarcal =  struct.pack("B", 0x02)
sensorMagOn = struct.pack("H", 0x0007)
sensorGyrOn = struct.pack("H", 0x0007)
sensorAccOn = struct.pack("H", 0x0038)

tag.IRtemperature.enable(sensorOn)
tag.humidity.enable(sensorOn)
tag.barometer.enable(sensorOn)
tag.accelerometer.enable(sensorAccOn)
# tag.magnetometer.enable(sensorMagOn)
# tag.gyroscope.enable(sensorGyrOn)
tag.luxometer.enable(sensorOn)

base_topic = 'jpmens/cc2650/%s' % my_sensor.replace(':', '').lower()

while True:
    msgs = []

    ambient_temp, target_temp = tag.IRtemperature.read()
    x_accel, y_accel, z_accel = tag.accelerometer.read()
    ambient_temp, rel_humidity = tag.humidity.read()
    lux = tag.luxometer.read()
    ambient_temp, pressure_millibars = tag.barometer.read()

    data = {
        'ambient_temp'  : ambient_temp,
        'target_temp'   : target_temp,
        'humidity'      : rel_humidity,
        'lux'           : lux,
        'millibars'     : pressure_millibars,
        'tst'           : int(time.time()),
    }

    payload = json.dumps(data)
    print payload
    msgs.append((base_topic, payload, 0, False))
    for k in data:
        msgs.append( ( "%s/%s" % (base_topic, k), data[k], 0, False ) )

    mqtt.multiple(msgs, hostname='test.mosquitto.org')

    time.sleep(60)

tag.disconnect()
