#!/usr/bin/env python

'''
Playing around with CoreWLAN to return information about the wi-fi connection

Documentation:
https://developer.apple.com/library/mac/documentation/CoreWLAN/Reference/CWInterface_reference/translated_content/CWInterface.html
'''
import objc

objc.loadBundle('CoreWLAN',
				bundle_path='/System/Library/Frameworks/CoreWLAN.framework',
				module_globals=globals())

class WiFi(object):
	'''	WiFI object'''

	def __init__(self):
		self.wifi = CWInterface.interfaceNames()
		for iname in self.wifi:
			self.interface = CWInterface.interfaceWithName_(iname)

	def get_wifistatus(self):
		if self.interface.powerOn() == 1:
			return "Yes"
		return "No"

	def get_ssid(self):
		return self.interface.ssid()

	def get_interface(self):
		return self.interface.interfaceName()

	def get_hardwareaddress(self):
		return self.interface.hardwareAddress()

	def get_aggregatenoise(self):
		return self.interface.aggregateNoise()

	def get_aggregaterssi(self):
		return self.interface.aggregateRSSI()

	def get_bssid(self):
		return self.interface.bssid()

	def get_channel(self):
		return self.interface.channel()

	def get_transmitrate(self):
		return self.interface.transmitRate()

	def get_mcsindex(self):
		return self.interface.mcsIndex()

def main():
	wifi = WiFi()
	print 'Interface: %s' % wifi.get_interface()
	print 'Hardware Address: %s' % wifi.get_hardwareaddress()
	print 'Active: %s' % wifi.get_wifistatus()
	print 'SSID: %s' % wifi.get_ssid()
	print 'Aggregate Noise: %s' % wifi.get_aggregatenoise()
	print 'BSSID: %s' % wifi.get_bssid()
	print 'RSSI: %s' % wifi.get_aggregaterssi()
	print 'Channel: %s' % wifi.get_channel()
	print 'Transmit Rate: %s' % wifi.get_transmitrate()
	print 'MCS Index: %s' % wifi.get_mcsindex()

if __name__ == "__main__":
	main()
