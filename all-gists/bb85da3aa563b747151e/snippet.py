# coding: utf-8
 
import smbus
import time
import urllib2, json, requests
 
INTERVAL = 60*1 # second
ADDRESS = 0x48
CHANNEL = 1

API_KEY = "{X-ApiKey}"
FEED_ID = "{Feed ID}"
 
class ADT7410:
    def __init__(self, address, channel):
        self.address = address
        self.channel = channel
 
    # read from ADT7410
    def readValue(self):
        try:
            data = smbus.SMBus(self.channel).read_i2c_block_data(self.address, 0x00, 2)
            temp = (data[0] << 8 | data[1]) >> 3
            if(temp >= 4096):
                temp -= 8192
            value = temp * 0.0625
            return value
        except Exception as e:
            print str(e)
            return None
 
    # regist to xively
    def registToXively(self, apiKey, feedId):
        request = { 'datastreams' : [ {'id' : 'Temperature', 'current_value' : self.readValue()}]}
        requestJson = json.dumps(request)
        url = "https://api.xively.com/v2/feeds/" + feedId + ".json"
        headers = {"X-ApiKey": apiKey}
        res = requests.put(url, headers=headers, data=requestJson)
        return res
 
sensor = ADT7410(ADDRESS, CHANNEL)
 
while True:
    value = sensor.readValue()
    if value is not None:
        print("Temperature: %6.2f [Deg. C.]" %value)
        sensor.registToXively(API_KEY, FEED_ID)
    time.sleep(INTERVAL)