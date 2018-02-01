import socket
import struct
import binascii
import time
import json
import urllib2

# Use your own IFTTT key, not this fake one
ifttt_key = '9cn3847ntc8394tn8-ab'
# Set these up at https://ifttt.com/maker
ifttt_url_poop = 'https://maker.ifttt.com/trigger/baby_pooped/with/key/' + ifttt_key
ifttt_url_pee = 'https://maker.ifttt.com/trigger/baby_peed/with/key/' + ifttt_key

# Replace these fake MAC addresses and nicknames with your own
macs = {
    '34545555e7ad' : 'chromebook',
    '48d703450d65' : 'macbook',
    'ec3454354536' : 'nexus6',
    '2c3453455541' : 'apple_tv',
    '6c7092236348' : 'airport_express',
    '74234223434a' : 'dash_glad',
    '7234234417c2' : 'dash_tide'
}

# Trigger a IFTTT URL. Body includes JSON with timestamp values.
def trigger_url(url):
    data = '{ "value1" : "' + time.strftime("%Y-%m-%d") + '", "value2" : "' + time.strftime("%H:%M") + '" }'
    req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
    f = urllib2.urlopen(req)
    response = f.read()
    f.close()
    return response

def record_poop():
    print 'triggering poop event, response: ' + trigger_url(ifttt_url_poop)

def record_pee():
    print 'triggering pee event, response: ' + trigger_url(ifttt_url_pee)

rawSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))

while True:
    packet = rawSocket.recvfrom(2048)
    ethernet_header = packet[0][0:14]
    ethernet_detailed = struct.unpack("!6s6s2s", ethernet_header)
    # skip non-ARP packets
    ethertype = ethernet_detailed[2]
    if ethertype != '\x08\x06':
        continue
    # read out data
    arp_header = packet[0][14:42]
    arp_detailed = struct.unpack("2s2s1s1s2s6s4s6s4s", arp_header)
    source_mac = binascii.hexlify(arp_detailed[5])
    source_ip = socket.inet_ntoa(arp_detailed[6])
    dest_ip = socket.inet_ntoa(arp_detailed[8])
    if source_mac in macs:
        #print "ARP from " + macs[source_mac] + " with IP " + source_ip
        if macs[source_mac] == 'dash_glad':
            record_poop()
        if macs[source_mac] == 'dash_tide':
            record_pee()
    else:
        print "Unknown MAC " + source_mac + " from IP " + source_ip
