#!/usr/bin/env python
# September 2013
# by Matthew Bordignon, @bordignon on Twitter
#
# Simple Python script (v2.7x) that subscribes to a MQTT broker topic and inserts the topic into a mysql database
# This is designed for the http://mqttitude.org/ project backend
#

import MySQLdb
import mosquitto
import json
import time

#mosquitto broker config
broker = 'mqtt.localdomain'
broker_port = 1883
broker_topic = '/test/location/#'
#broker_clientid = 'mqttuide2mysqlScript'
#mysql config
mysql_server = 'thebeast.localdomain'
mysql_username = 'root'
mysql_passwd = ''
mysql_db = 'mqtt'
#change table below.

# Open database connection
db = MySQLdb.connect(mysql_server, mysql_username, mysql_passwd, mysql_db)
# prepare a cursor object using cursor() method
cursor = db.cursor()

def on_connect(mosq, obj, rc):
    print("rc: "+str(rc))

def on_message(mosq, obj, msg):
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    vars_to_sql = []
    keys_to_sql = []
    list = []
    
    list = json.loads(msg.payload)
    
    for key,value in list.iteritems():
      print ("")
      print key, value
      if key == 'tst':
        print "time found"
        print value
        value = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(value)))
        print value
        
      value_type = type(value)
      if value_type is not dict:
        print "value_type is not dict"
        if value_type is unicode:
          print "value_type is unicode"
          vars_to_sql.append(value.encode('ascii', 'ignore'))
          keys_to_sql.append(key.encode('ascii', 'ignore'))
        else:
          print "value_type is not unicode"
          vars_to_sql.append(value)
          keys_to_sql.append(key)
    #add the msg.topic to the list as well
    print "topic", msg.topic
    addtopic = 'topic'
    vars_to_sql.append(msg.topic.encode('ascii', 'ignore'))
    keys_to_sql.append(addtopic.encode('ascii', 'ignore'))
    
    keys_to_sql = ', '.join(keys_to_sql)

    try:
       # Execute the SQL command 
       # change locations to the table you are using
       queryText = "INSERT INTO locations(%s) VALUES %r"
       queryArgs = (keys_to_sql, tuple(vars_to_sql))
       cursor.execute(queryText % queryArgs)
       print('Successfully Added record to mysql')
       db.commit()
    except MySQLdb.Error, e:
        try:
            print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
        except IndexError:
            print "MySQL Error: %s" % str(e)
        # Rollback in case there is any error
        db.rollback()
        print('ERROR adding record to MYSQL')

def on_publish(mosq, obj, mid):
    print("mid: "+str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_log(mosq, obj, level, string):
    print(string)

# If you want to use a specific client id, use
#mqttc = mosquitto.Mosquitto(broker_clientid)
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.
mqttc = mosquitto.Mosquitto()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
# Uncomment to enable debug messages
mqttc.on_log = on_log

mqttc.connect(broker, broker_port, 60)
mqttc.subscribe(broker_topic, 0)

rc = 0
while rc == 0:
    rc = mqttc.loop()

print("rc: "+str(rc))

# disconnect from server
print ('Disconnected, done.')
db.close()