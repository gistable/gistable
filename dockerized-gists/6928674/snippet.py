from scapy.all import *

answer = sr1(IP(dst="8.8.8.8")/UDP(dport=53)/DNS(rd=1,qd=DNSQR(qname="www.thepacketgeek.com")),verbose=0)
print answer[DNS].summary()