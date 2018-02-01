#Begin
#!/usr/local/bin/python

#import httplib
import urllib
from google.appengine.api import urlfetch

from struct import *

def cellid_2_pos(cellid, lac, mnc = 0, mcc = 0):
	pd = chr(0)+chr(0x15) # Function Code?
	pd += chr(0)+chr(0)+chr(0)+chr(0)+chr(0)+chr(0)+chr(0)+chr(0) #Session ID?
	pd += chr(0)+chr(0x02)+chr(0x62)+chr(0x72) # Contry Code
	pd += chr(0)+chr(0x12)+chr(0x53)+chr(0x6f)+chr(0x6e) # User Agent
	pd += chr(0x79)+chr(0x5f)+chr(0x45)+chr(0x72)+chr(0x69) # User Agent
	pd += chr(0x63)+chr(0x73)+chr(0x73)+chr(0x6f)+chr(0x6e) # User Agent
	pd += chr(0x2d)+chr(0x4b)+chr(0x37)+chr(0x35)+chr(0x30) # User Agent
	pd += chr(0)+chr(0x05)+chr(0x31)+chr(0x2e)+chr(0x33)+chr(0x2e)+chr(0x31) # version
	pd += chr(0)+chr(0x03)+chr(0x57)+chr(0x65)+chr(0x62) # "Web"
	pd += chr(0x1b) # Op Code?
	pd += chr((mnc >> 24) & 0xFF) + chr((mnc >> 16) & 0xFF) + chr((mnc >> 8) & 0xFF) + chr(mnc & 0xFF) # MNC
	pd += chr((mcc >> 24) & 0xFF) + chr((mcc >> 16) & 0xFF) + chr((mcc >> 8) & 0xFF) + chr(mcc & 0xFF) # MCC
	pd += chr(0)+chr(0)+chr(0)+chr(0x03) # ??
	pd += chr(0)+chr(0) # ??
	pd += chr((cellid >> 24) & 0xFF) + chr((cellid >> 16) & 0xFF) + chr((cellid >> 8) & 0xFF) + chr(cellid & 0xFF) # CID - replace 0x00 with the hex value from CID
	pd += chr((lac    >> 24) & 0xFF) + chr((lac    >> 16) & 0xFF) + chr((lac    >> 8) & 0xFF) + chr(lac    & 0xFF) # LAC - replace 0x00 with the hex value from LAC
	pd += chr(0)+chr(0)+chr(0)+chr(0) # ??
	pd += chr(0)+chr(0)+chr(0)+chr(0) # ??
	pd += chr(0)+chr(0)+chr(0)+chr(0) # ??
	pd += chr(0)+chr(0)+chr(0)+chr(0) # ??
	
	headers = {"Content-type": "application/binary"}
	
	
	response = urlfetch.fetch("http://www.google.com/glm/mmap",
                        	pd,
                        	urlfetch.POST,
                        	headers)
	
	data = response.content
	if response.status_code != 200:
		return False
	
	lat = unpack('>l',data[7:11])[0]/1000000.0
	lon = unpack('>l',data[11:15])[0]/1000000.0
	return [lat, lon]
# End Python 2.5

