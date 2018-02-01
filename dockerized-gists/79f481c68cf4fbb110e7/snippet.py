from scapy.all import *
import requests
import time
MAGIC_FORM_URL = 'http://put-your-url-here'

def record_poop():
  data = {
    "Timestamp": time.strftime("%Y-%m-%d %H:%M"), 
    "Measurement": 'Poopy Diaper'
  }
  requests.post(MAGIC_FORM_URL, data)

def record_wake():
  data = {
    "Timestamp": time.strftime("%Y-%m-%d %H:%M"), 
    "Measurement": 'Woke from Sleep'
  }
  requests.post(MAGIC_FORM_URL, data)

def arp_display(pkt):
  timestamp = time.strftime("%Y-%m-%d %H:%M")
  if pkt[ARP].op == 1: #who-has (request)
    if pkt[ARP].psrc == '0.0.0.0': # ARP Probe
      if pkt[ARP].hwsrc == '74:75:48:5f:99:30': # Huggies        
        print "Pushed Huggies"
        record_poop()
      elif pkt[ARP].hwsrc == '10:ae:60:00:4d:f3': # Elements
        print "Pushed Elements"
        record_wake()
      else:
        print "ARP Probe from unknown device: " + pkt[ARP].hwsrc

print sniff(prn=arp_display, filter="arp", store=0, count=10)
 