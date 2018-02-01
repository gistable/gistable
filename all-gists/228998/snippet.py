#!/usr/bin/env python
# encoding: utf-8

import socket
from struct import *
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import math

UDP_IP="127.0.0.1"
UDP_PORT=49045 # I'm not sure if there's a default so you'll have to set it like this: http://dronedynamics.com/xplane_config.png
UDP_SENDTO_PORT=49000 # This is the port X-Plane is listening on for commands (such as the data select packet we send to tell it what data to send us).

class XplaneConnector(DatagramProtocol):
    def __init__(self):
        """
        This will send a packet to X-Plane to select the data you need to read.
        Once it's sent X-Plane will output data automatically at a default of 20Hz.
        In this string, "\x03\x00\x00\x00", we are selecting the third checkbox in the
        "Settings" > "Data Input and Output" menu item ("speeds" in this example). And
        don't forget that these numbers are in hexadecimal!
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((UDP_IP,49999)) # this is the port we're sending from and it doesn't really matter
        data_selection_packet = "DSEL0" # this is the xplane packet type
        data_selection_packet += "\x03\x00\x00\x00" # airspeed
        data_selection_packet += "\x04\x00\x00\x00" # accelerometers
        data_selection_packet += "\x06\x00\x00\x00" # temperature
        data_selection_packet += "\x11\x00\x00\x00" # gyros
        data_selection_packet += "\x12\x00\x00\x00" # pitch and roll (for sanity check)
        data_selection_packet += "\x14\x00\x00\x00" # altimeter and GPS
        self.sock.sendto(data_selection_packet,(UDP_IP,UDP_SENDTO_PORT))

    def datagramReceived(self, data, (host, port)):
        """
        We've received a UDP packet from X-Plane (which is in binary so printing it
        won't help). This is where we unpack and then do whatever with the data.
        """
        self.unpack(data)
        self.display()
        # self.log() # uncomment this line if you want to log to a file

    def unpack(self, data):
        """
        When we receive a UDP packet from X-Plane we'll need to unpack the data.
        See http://www.grc.nasa.gov/WWW/K-12/airplane/rotations.html for which body
        axes are which (please don't invent your own). X-Plane gives some of the data
        in a funny order (q before p and r?!).
        """
        self.Vair = unpack_from('<f', data, 9)[0]
        self.Vtgs = unpack_from('<f', data, 9+12)[0]
        self.az = unpack_from('<f', data, 9+16+36)[0]
        self.ax = unpack_from('<f', data, 9+20+36)[0]
        self.ay = unpack_from('<f', data, 9+24+36)[0]
        self.temperature = unpack_from('<f', data, 9+72+0)[0]
        self.q = math.radians(unpack_from('<f', data, 9+108+0)[0])
        self.p = math.radians(unpack_from('<f', data, 9+108+4)[0])
        self.r = math.radians(unpack_from('<f', data, 9+108+8)[0])
        self.pitch = math.radians(unpack_from('<f', data, 9+144+0)[0])
        self.roll = math.radians(unpack_from('<f', data, 9+144+4)[0])
        self.altitude = unpack_from('<f', data, 9+180+20)[0]
        self.latitude = unpack_from('<f', data, 9+180+0)[0]
        self.longitude = unpack_from('<f', data, 9+180+4)[0]

    def display(self):
        """
        Use the curses library if you want to format and update the data nicely on the
        screen (similar to the "top" command in *nix)
        """
        print "%f, %f, %f, %f, %f, %f, %f, %f, %f, %f" % (self.Vair, self.ax, self.ay, self.az, self.p, self.q, self.r, self.altitude, self.latitude, self.longitude)

    def log(self):
        """
        Yeah I'll get to file logging later but for now you can do it yourself (delete the "pass" line).
        """
        pass

if __name__ == "__main__":
    """
    If you call this file directly (from the command line using "python xplane.py") then
    it will sleep until a packet is received and then call datagramReceived when one arrives.
    """
    print "Listening to X-Plane..."
    xplane_connector = XplaneConnector()
    reactor.listenUDP(UDP_PORT, xplane_connector)
    reactor.run()
