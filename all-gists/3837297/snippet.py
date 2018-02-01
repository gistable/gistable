$~ sudo scapy

>>> from datetime import datetime
>>> pkt = IP(dst="www.google.com", ttl=1) / ICMP()
>>> ans,unans = sr(pkt*3)
Begin emission:
.**Finished to send 3 packets.
*
Received 4 packets, got 3 answers, remaining 0 packets
>>> sent = datetime.fromtimestamp(ans[0][0].sent_time)
>>> received = datetime.fromtimestamp(ans[0][1].time)
>>> print (received-sent)
0:00:00.001820
