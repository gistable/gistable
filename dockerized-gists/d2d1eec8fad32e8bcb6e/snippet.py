from scapy.all import *
def arp_display(pkt):
  if pkt[ARP].op == 1: #who-has (request)
    if pkt[ARP].psrc == '0.0.0.0': # ARP Probe
      if pkt[ARP].hwsrc == '74:75:48:5f:99:30': # Huggies
        print "Pushed Huggies"
      elif pkt[ARP].hwsrc == '10:ae:60:00:4d:f3': # Elements
        print "Pushed Elements"
      else:
        print "ARP Probe from unknown device: " + pkt[ARP].hwsrc

print sniff(prn=arp_display, filter="arp", store=0, count=10)
 