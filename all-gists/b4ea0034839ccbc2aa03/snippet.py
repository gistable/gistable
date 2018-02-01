#!/usr/bin/python
from mosquitto import Mosquitto 

publish_key = "demo" 
subscribe_key = "demo" 
channel_name = "F" 
client_uuid = "2fb96def5" 
mqtt_hostname = "mqtt.pubnub.com" 
mqtt_connect = publish_key + "/" + subscribe_key + "/" + client_uuid 
mqtt_topic = publish_key + "/" + subscribe_key + "/" + channel_name 
mosq_object = Mosquitto(mqtt_connect) 

def on_message( mosq, obj, msg ):
    print( msg.payload, msg.topic )

mosq_object.on_message = on_message
mosq_object.connect(mqtt_hostname)
mosq_object.publish( mqtt_topic, "Hello World!" )
mosq_object.subscribe(mqtt_topic)
mosq_object.loop_forever()
