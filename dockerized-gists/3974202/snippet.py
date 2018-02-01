#! /usr/bin/python

import socket,time,string,random,thread

m_Vars = {
	"bufLen" : 1024 * 10,
	"defaultServerIp" : "192.168.1.100",
	"defaultServerPort" : 554,
	"defaultTestUrl" : "rtsp://192.168.1.100/test1.mp4",
	"defaultUserAgent" : "LibVLC/2.0.3 (LIVE555 Streaming Media v2011.12.23)"
}

def genmsg_OPTIONS(url,seq,userAgent):
	msgRet = "OPTIONS " + url + " RTSP/1.0\r\n"
	msgRet += "CSeq: " + str(seq) + "\r\n"
	msgRet += "User-Agent: " + userAgent + "\r\n"
	msgRet += "\r\n"
	return msgRet

def genmsg_DESCRIBE(url,seq,userAgent):
	msgRet = "DESCRIBE " + url + " RTSP/1.0\r\n"
	msgRet += "CSeq: " + str(seq) + "\r\n"
	msgRet += "User-Agent: " + userAgent + "\r\n"
	msgRet += "Accept: application/sdp\r\n"
	msgRet += "\r\n"
	return msgRet

def genmsg_SETUP(url,seq,userAgent):
	msgRet = "SETUP " + url + " RTSP/1.0\r\n"
	msgRet += "CSeq: " + str(seq) + "\r\n"
	msgRet += "User-Agent: " + userAgent + "\r\n"
	msgRet += "Transport: RTP/AVP/TCP;unicast;interleaved=0-1\r\n"
	msgRet += "\r\n"
	return msgRet

def genmsg_SETUP2(url,seq,userAgent,sessionId):
	msgRet = "SETUP " + url + " RTSP/1.0\r\n"
	msgRet += "CSeq: " + str(seq) + "\r\n"
	msgRet += "User-Agent: " + userAgent + "\r\n"
	msgRet += "Transport: RTP/AVP/TCP;unicast;interleaved=2-3\r\n"
	msgRet += "Session: " + sessionId + "\r\n"
	msgRet += "\r\n"
	return msgRet

def genmsg_PLAY(url,seq,userAgent,sessionId):
	msgRet = "PLAY " + url + " RTSP/1.0\r\n"
	msgRet += "CSeq: " + str(seq) + "\r\n"
	msgRet += "User-Agent: " + userAgent + "\r\n"
	msgRet += "Session: " + sessionId + "\r\n"
	msgRet += "\r\n"
	return msgRet

def genmsg_TEARDOWN(url,seq,userAgent,sessionId):
	msgRet = "TEARDOWN " + url + " RTSP/1.0\r\n"
	msgRet += "CSeq: " + str(seq) + "\r\n"
	msgRet += "User-Agent: " + userAgent + "\r\n"
	msgRet += "Session: " + sessionId + "\r\n"
	msgRet += "\r\n"
	return msgRet

def decodeMsg(strContent):
	mapRetInf = {}		
	for str in [elem for elem in strContent.split("\n") if len(elem) > 1][2:-1]:
		#print str
		tmp2 = str.split(":")
		mapRetInf[tmp2[0]]=tmp2[1][:-1]
	#print mapRetInf		
	return mapRetInf
	

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((m_Vars["defaultServerIp"],m_Vars["defaultServerPort"]))	
seq  = 1

print genmsg_OPTIONS(m_Vars["defaultTestUrl"],seq,m_Vars["defaultUserAgent"])
s.send(genmsg_OPTIONS(m_Vars["defaultTestUrl"],seq,m_Vars["defaultUserAgent"]))
print s.recv(m_Vars["bufLen"])
seq = seq + 1

s.send(genmsg_DESCRIBE(m_Vars["defaultTestUrl"],seq,m_Vars["defaultUserAgent"]))
msg1 = s.recv(m_Vars["bufLen"])
print msg1	
seq = seq + 1

s.send(genmsg_SETUP(m_Vars["defaultTestUrl"] + "/trackID=3",seq,m_Vars["defaultUserAgent"]))
msg1 = s.recv(m_Vars["bufLen"])
print msg1	
seq = seq + 1

sessionId = decodeMsg(msg1)['Session']

s.send(genmsg_SETUP2(m_Vars["defaultTestUrl"] + "/trackID=4",seq,m_Vars["defaultUserAgent"],sessionId))
msg1 = s.recv(m_Vars["bufLen"])
print msg1	
seq = seq + 1

s.send(genmsg_PLAY(m_Vars["defaultTestUrl"] + "/",seq,m_Vars["defaultUserAgent"],sessionId))
msg1 = s.recv(m_Vars["bufLen"])
print msg1	
seq = seq + 1

while True :
	#s.send(genmsg_ANNOUNCE(m_Vars["defaultServerIp"]))
	msgRcv = s.recv(m_Vars["bufLen"])
	if 0 == len(msgRcv) : break
	print len(msgRcv)
	#time.sleep(5)

s.send(genmsg_TEARDOWN(m_Vars["defaultTestUrl"] + "/",seq,m_Vars["defaultUserAgent"],sessionId))
msg1 = s.recv(m_Vars["bufLen"])
print msg1	

s.close()
