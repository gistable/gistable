#!/usr/bin/python2

"""
    Use scapy to modify packets going through your machine.
    Based on nfqueue to block packets in the kernel and pass them to scapy for validation
"""

import nfqueue
from scapy.all import *
import os

# All packets that should be filtered :

# If you want to use it as a reverse proxy for your machine
iptablesr = "iptables -A OUTPUT -j NFQUEUE"

# If you want to use it for MITM :
# iptablesr = "iptables -A FORWARD -j NFQUEUE"

print("Adding iptable rules :")
print(iptablesr)
os.system(iptablesr)

# If you want to use it for MITM attacks, set ip_forward=1 :
#print("Set ipv4 forward settings : ")
#os.system("sysctl net.ipv4.ip_forward=1")

def callback(payload):
    # Here is where the magic happens.
    data = payload.get_data()
    pkt = IP(data)
    print("Got a packet ! source ip : " + str(pkt.src))
    if pkt.src == "192.168.1.2":
        # Drop all packets coming from this IP
        print("Dropped it. Oops")
        payload.set_verdict(nfqueue.NF_DROP)
    else:
        # Let the rest go it's way
        payload.set_verdict(nfqueue.NF_ACCEPT)
    # If you want to modify the packet, copy and modify it with scapy then do :
    #payload.set_verdict_modified(nfqueue.NF_ACCEPT, str(packet), len(packet))


def main():
    # This is the intercept
    q = nfqueue.queue()
    q.open()
    q.bind(socket.AF_INET)
    q.set_callback(callback)
    q.create_queue(0)
    try:
        q.try_run() # Main loop
    except KeyboardInterrupt:
        q.unbind(socket.AF_INET)
        q.close()
        print("Flushing iptables.")
        # This flushes everything, you might wanna be careful
        os.system('iptables -F')
        os.system('iptables -X')


if __name__ == "__main__":
    main()
