#!/usr/bin/python

# Script to poll the UPS (via apcupsd) and publish interesting facts to
# MQTT. 

# Published under GPL3+ by Andrew Elwell <Andrew.Elwell@gmail.com>


import subprocess
# we use mosquitto for the MQTT part
import mosquitto


# which status messages to publish. We use upsname as part of the topic
interesting = ('status', 'linev', 'loadpct', 'battv', 'bcharge')
apc_status = {}

res = subprocess.check_output("/sbin/apcaccess")
for line in res.split('\n'):
    (key,spl,val) = line.partition(': ')
    key = key.rstrip().lower()
    # tempted to also remove units from val also
    val = val.strip()
    apc_status[key] = val
    #print "K:%s V:%s" % (key,val)


def on_connect(rc):
	print "rc: ", rc

def on_message(msg):
	print msg.topic,msg.qos,msg.payload

def on_publish(mid):
	print "mid:", mid

def on_subscribe(mid, granted_qos):
	print "Subscribed:",mid,granted_qos
	

mqttc = mosquitto.Mosquitto("python_pub")
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
mqttc.connect("test.mosquitto.org", 1883, 60, True)
# mqttc.subscribe("$SYS/#", 0)

for thing in interesting:
    #print ">K:%s V:%s<" % (thing,apc_status[thing])
    #print "/apc/%s/%s %s" % (apc_status['upsname'],thing,apc_status[thing])
    mqttc.publish("apc/%s/%s" % (apc_status['upsname'],thing), apc_status[thing])
