#Original code by Adafruit
 
import os
import glob
import time
 
from twilio.rest import TwilioRestClient
 
client = TwilioRestClient(account='abc', token='123')
 
MAX_F_TEMP = 80
 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
 
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f
	
while True:
    c, f = read_temp()
    if f > MAX_F_TEMP:
    	client.messages.create(to='+170355555555', 
    		from_='+12025555555', 
    		body="fish tank overheating!!")
    		time.sleep(500)
	# print(read_temp())
	time.sleep(1)