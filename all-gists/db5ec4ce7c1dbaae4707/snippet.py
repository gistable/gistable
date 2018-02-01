import time
import sys
import logging
import pychromecast
from scapy.all import *

mac_address = '00:00:00:00:00:00'
def arp_display(pkt):
    if pkt[ARP].op == 1:
        if pkt[ARP].hwsrc == mac_address:
			
            if '--show-debug' in sys.argv:
                logging.basicConfig(level=logging.DEBUG)

            cast = pychromecast.get_chromecast(friendly_name="CHROMECAST_NAME")
            while cast == None:
                cast = pychromecast.get_chromecast(friendly_name="CHROMECAST_NAME")

            try:
                if not cast.is_idle:
                    print("Killing current running app")
                    cast.quit_app()
                    time.sleep(5)
            except:
                pass
            print("Playing media")
            cast.play_media(("url"), "audio/mp3")

while(True):
    sniff(prn=arp_display, filter="arp", store=0, count=10)