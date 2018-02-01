#!/usr/bin/python
import socket, ssl, select, time, re
from thread import start_new_thread
from struct import pack

TYPE_ENUM = 0
TYPE_STRING = 2
TYPE_BYTES = TYPE_STRING

def clean(s):
	return re.sub(r'[\x00-\x1F\x7F]', '?',s)
def getType(fieldId,t):
	return (fieldId << 3) | t
def getLenOf(s):
	x = ""
	l = len(s)
	while(l > 0x7F):
		x += pack("B",l & 0x7F | 0x80)
		l >>= 7
	x += pack("B",l & 0x7F)
	return x

protocolVersion = 0
source_id = "sender-0"
destination_id = "receiver-0"
chromecast_server = "192.168.178.27"


socket = socket.socket()
socket = ssl.wrap_socket(socket)
print "connecting ..."

socket.connect((chromecast_server,8009))

payloadType = 0 #0=string
data = "{\"type\":\"CONNECT\",\"origin\":{}}"
lnData = getLenOf(data)
print len(lnData),len(data),lnData.encode("hex")
namespace = "urn:x-cast:com.google.cast.tp.connection"
msg = pack(">BBBB%dsBB%dsBB%dsBBB%ds%ds" % (len(source_id),len(destination_id),len(namespace),len(lnData),len(data)),getType(1,TYPE_ENUM),protocolVersion,getType(2,TYPE_STRING),len(source_id),source_id,getType(3,TYPE_STRING),len(destination_id),destination_id,getType(4,TYPE_STRING),len(namespace),namespace,getType(5,TYPE_ENUM),payloadType,getType(6,TYPE_BYTES),lnData,data)
msg = pack(">I%ds" % (len(msg)),len(msg),msg)
print msg.encode("hex")
print "sending ..."
socket.write(msg)

payloadType = 0 #0=string
data = "{\"type\":\"GET_STATUS\",\"requestId\":46479000}"
lnData = getLenOf(data)
namespace = "urn:x-cast:com.google.cast.receiver"
msg = pack(">BBBB%dsBB%dsBB%dsBBB%ds%ds" % (len(source_id),len(destination_id),len(namespace),len(lnData),len(data)),getType(1,TYPE_ENUM),protocolVersion,getType(2,TYPE_STRING),len(source_id),source_id,getType(3,TYPE_STRING),len(destination_id),destination_id,getType(4,TYPE_STRING),len(namespace),namespace,getType(5,TYPE_ENUM),payloadType,getType(6,TYPE_BYTES),lnData,data)
msg = pack(">I%ds" % (len(msg)),len(msg),msg)
print "sending ..."
socket.write(msg)

m=None
result=""
while m==None:
	lastresult = socket.read(2048)
	result += lastresult
	print "#"+lastresult.encode("hex")
	print clean("!"+lastresult)
	m = re.search('"sessionId":"(?P<session>[^"]+)"', result)
	print "#%i" % (m==None)

print "session:",m.group("session")
session = m.group("session")


payloadType = 0 #0=string
data = "{\"type\":\"LAUNCH\",\"requestId\":46479001,\"appId\":\"CC1AD845\"}"
lnData = getLenOf(data)
namespace = "urn:x-cast:com.google.cast.receiver"
msg = pack(">BBBB%dsBB%dsBB%dsBBB%ds%ds" % (len(source_id),len(destination_id),len(namespace),len(lnData),len(data)),getType(1,TYPE_ENUM),protocolVersion,getType(2,TYPE_STRING),len(source_id),source_id,getType(3,TYPE_STRING),len(destination_id),destination_id,getType(4,TYPE_STRING),len(namespace),namespace,getType(5,TYPE_ENUM),payloadType,getType(6,TYPE_BYTES),lnData,data)
msg = pack(">I%ds" % (len(msg)),len(msg),msg)
print msg.encode("hex")
print "sending ..."
socket.write(msg)

m=None
result=""
while m==None:
	lastresult = socket.read(2048)
	result += lastresult
	print "#"+lastresult.encode("hex")
	print clean("!"+lastresult)
	m = re.search('"transportId":"(?P<transportId>[^"]+)"', result)
destination_id = m.group("transportId")
print destination_id

payloadType = 0 #0=string
data = "{\"type\":\"CONNECT\",\"origin\":{}}"
lnData = getLenOf(data)
print len(lnData),len(data),lnData.encode("hex")
namespace = "urn:x-cast:com.google.cast.tp.connection"
msg = pack(">BBBB%dsBB%dsBB%dsBBB%ds%ds" % (len(source_id),len(destination_id),len(namespace),len(lnData),len(data)),getType(1,TYPE_ENUM),protocolVersion,getType(2,TYPE_STRING),len(source_id),source_id,getType(3,TYPE_STRING),len(destination_id),destination_id,getType(4,TYPE_STRING),len(namespace),namespace,getType(5,TYPE_ENUM),payloadType,getType(6,TYPE_BYTES),lnData,data)
msg = pack(">I%ds" % (len(msg)),len(msg),msg)
print msg.encode("hex")
print "sending ..."
socket.write(msg)

payloadType = 0 #0=string
#data = "{\"type\":\"LOAD\",\"requestId\":46479002,\"sessionId\":\""+session+"\",\"media\":{\"contentId\":\"http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4\",\"streamType\":\"buffered\",\"contentType\":\"video/mp4\"},\"autoplay\":true,\"currentTime\":0,\"customData\":{\"payload\":{\"title:\":\"Big Buck Bunny\",\"thumb\":\"images/BigBuckBunny.jpg\"}}}"
data = "{\"type\":\"LOAD\",\"requestId\":46479002,\"sessionId\":\""+session+"\",\"media\":{\"contentId\":\"http://origintest.cloudapp.net/media/SintelTrailer_Smooth_from_WAME_720p_Main_Profile/sintel_trailer-720p.ism/manifest\",\"streamType\":\"buffered\",\"contentType\":\"application/vnd.ms-sstr+xml\"},\"autoplay\":true,\"currentTime\":0,\"customData\":{\"payload\":{\"title:\":\"\"}}}"

lnData = getLenOf(data)
namespace = "urn:x-cast:com.google.cast.media"
msg = pack(">BBBB%dsBB%dsBB%dsBBB%ds%ds" % (len(source_id),len(destination_id),len(namespace),len(lnData),len(data)),getType(1,TYPE_ENUM),protocolVersion,getType(2,TYPE_STRING),len(source_id),source_id,getType(3,TYPE_STRING),len(destination_id),destination_id,getType(4,TYPE_STRING),len(namespace),namespace,getType(5,TYPE_ENUM),payloadType,getType(6,TYPE_BYTES),lnData,data)
msg = pack(">I%ds" % (len(msg)),len(msg),msg)
print msg.encode("hex")
print "sending ..."
print "LOADING"
socket.write(msg)

try:
	while True:
		lastresult = socket.read(2048)
		if lastresult!="":
			print "#"+lastresult.encode("hex")
			print clean("!"+lastresult)
finally:
	socket.close()
	print "socket closed"
