#!/usr/bin/env python

# dump the contents of an atmel AT45DB041B flash part to 'data.bin'

# usage: ./dump_AT45DB041B.py /dev/ttyUSB0

# tested w/ https://github.com/audiohacked/pyBusPirate ac19e00b53, Bus Pirate Hardware labelled v3.6, Firmware: "Bus Pirate v3b, Firmware v5.10 (r559), Bootloader v4.4"

# bugs: slow. as in... dozens of hours :/

# note: flashrom may support this chip, i did this as a learning exercise.

# reference:
#  http://dangerousprototypes.com/docs/AT45DB041D_4Mbit_flash_memory (note -B model lacks chip ID query feature)
#  https://github.com/mysmartgrid/hexasense/wiki/AT45-Data-Flash
#  http://dangerousprototypes.com/docs/SPI_(binary)
#  http://www.atmel.com/images/doc3443.pdf

import sys
from pyBusPirate.BinaryMode.SPI import *
def main(argv=None):

	f=open('data.bin', 'wb')
	spi = SPI(sys.argv[1], 115200)
	print "Entering binmode: ",
	if spi.BBmode():
		print "OK."
	else:
		print "failed."
		sys.exit()

	print "Entering raw SPI mode: ",
	if spi.enter_SPI():
		print "OK."
	else:
		print "failed."
		sys.exit()
		
	print "Configuring SPI."
	if not spi.cfg_pins(PinCfg.POWER | PinCfg.CS):
		print "Failed to set SPI peripherals."
		sys.exit()
	if not spi.set_speed(SPISpeed._8MHZ): # AT45DB041B has 20mhz max clock freq
		print "Failed to set SPI Speed."
		sys.exit()
	if not spi.cfg_spi(SPICfg.CLK_EDGE | SPICfg.OUT_TYPE):
		print "Failed to set SPI configuration.";
		sys.exit()
	spi.timeout(0.1)
	
	print "Reading Status register (should be 0x9C). See section 5.1.4 'Status Register Read' in the datasheet."
	spi.CS_Low()
	d=spi.bulk_trans(2, [0xD7,0x00])
	spi.CS_High()
	print "%02X\n" % ord(d[1])

	print "Reading first n bytes of flash. See section 5.1.1 'Continuous Array Read' in the datasheet."
	spi.CS_Low()
	spi.bulk_trans(8, [0xE8,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
	for i in range(33792): # 4325376/8==540672 bytes. 540672/264==2048 pages. 540672/16==33792 16-byte reads
		d=spi.bulk_trans(16, [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
		f.write(d)
		for each in d:
			print "%02X " % ord(each),
	spi.CS_High()
	f.close()
	print "\n"

	print "Reset Bus Pirate to user terminal: ",
	if spi.resetBP():
		print "OK."
	else:
		print "failed."
		sys.exit()
		

if __name__ == '__main__':
	sys.exit(main())
