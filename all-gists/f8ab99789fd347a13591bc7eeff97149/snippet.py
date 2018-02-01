# sudo apt-get install python-pip
# pip install paho-mqtt

import paho.mqtt.client as mqtt
import threading

def on_connect(mosq, obj, rc):
	print("rc: " + str(rc))

def on_message(mosq, obj, msg):
	print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def on_publish(mosq, obj, mid):
	print("mid: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
	print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
	print(string)

def send_payload():
	mqttc.publish("/topic", "PAYLOAD")

mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
mqttc.username_pw_set("USERNAME","PASSWORD")
mqttc.connect("SERVER URL", PORT)
mqttc.subscribe("/topic", 0)
mqttc.loop_start()

def main():
	while True:
		print "test"
		time.sleep(1)
		send_payload();
			
if __name__ == '__main__':
    main()

