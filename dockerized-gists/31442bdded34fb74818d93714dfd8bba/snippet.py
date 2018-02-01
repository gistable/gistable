#!/usr/bin/python
# -*- coding: utf-8 -*-
# SPI_MCP3304.py: read 8-channel ADC, based on http://www.havnemark.dk/?p=54 

# mcp3008_lm35.py - read an LM35 on CH0 of an MCP3008 on a Raspberry Pi
# mostly nicked from
#  http://jeremyblythe.blogspot.ca/2012/09/raspberry-pi-hardware- spi-analog-inp$
# Changed to work w. MCP3308 by Kim H. Rasmussen, June 2013
import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)

def readadc(adcnum):
	# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
	if adcnum > 7 or adcnum < 0:
		return -1

	# Frame format: 0000 1SCC | C000 000 | 000 000
	r = spi.xfer2([((adcnum & 6) >> 1)+12 , (adcnum & 1) << 7, 0])
	adcout = ((r[1] & 15) << 8) + r[2]

	# Read from ADC channels and convert the bits read into the voltage
	# Divisor changed from 1023 to 4095, due to 4 more bits
	return (adcout * 3.3) / 4095

while True:
	# Read all channels
	for i in range(8):
		print "%.4f" % (readadc(i)),
	print ""

	time.sleep(0.1)
