import serial
import time
from messaging.sms import SmsDeliver

ser=serial.Serial('/dev/ttyACM0', baudrate=9600, timeout=.1, rtscts=0)

def sendCommand(com):
	ser.write(com+"\r\n")
	time.sleep(2)
	ret = []
	while ser.inWaiting() > 0:
		msg = ser.readline().strip()
		msg = msg.replace("\r","")
		msg = msg.replace("\n","")
		if msg!="":
			ret.append(msg)
	return ret

def readSMS():
	print("LOOKING FOR SMS")
	list = sendCommand("AT+CMGL=0")
	ret = []
	for item in list:
		#print item
		if item.startswith("+CMGL:") == False:
			if item!="OK":
				ret.append(SmsDeliver(item))
	return ret

def killSMS():
	print("DELETING ALL MESSAGES")
	print sendCommand("AT+CMGD=1,1")

def main():
	return
	
	print("SENDING HELLO")
	com="ERROR"
	count=0
	while(com!="OK"):
		com=sendCommand("AT")[0]
		count+=1
		if(count>5):
			print "COULD NOT GET A HELLO, all I got was "+com
			return
	print("OK")
	
	print("CHANGING MESSAGE FORMAT")
	print(sendCommand("AT+CMGF=0")[0])
	while(True):
		sms = readSMS()
		
		for s in sms:
			print ""
			print "SMS"
			print s.text
			time.sleep(1)
		
		time.sleep(6)
		killSMS()

if __name__ == "__main__":
	if ser.isOpen():
		main()
	else:
		print "ERROR: CAN't OPEN CONNECTION"
	ser.close()