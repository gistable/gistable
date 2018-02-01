#!/usr/bin/python
#
#       MCP3204/MCP3208 sample program for Raspberry Pi
#
#       how to setup /dev/spidev?.?
#               $ suod modprobe spi_bcm2708
#
#       how to setup spidev
#               $ sudo apt-get install python-dev python-pip
#               $ sudo pip install spidev
#
import spidev
import time

class MCP3208:
        def __init__(self, spi_channel=0):
                self.spi_channel = spi_channel
                self.conn = spidev.SpiDev(0, spi_channel)
                self.conn.max_speed_hz = 1000000 # 1MHz

        def __del__( self ):
                self.close

        def close(self):
                if self.conn != None:
                        self.conn.close
                        self.conn = None

        def bitstring(self, n):
                s = bin(n)[2:]
                return '0'*(8-len(s)) + s

        def read(self, adc_channel=0):
                # build command
                cmd  = 128 # start bit
                cmd +=  64 # single end / diff
                if adc_channel % 2 == 1:
                        cmd += 8
                if (adc_channel/2) % 2 == 1:
                        cmd += 16
                if (adc_channel/4) % 2 == 1:
                        cmd += 32

                # send & receive data
                reply_bytes = self.conn.xfer2([cmd, 0, 0, 0])

                #
                reply_bitstring = ''.join(self.bitstring(n) for n in reply_bytes)
                # print reply_bitstring

                # see also... http://akizukidenshi.com/download/MCP3204.pdf (page.20)
                reply = reply_bitstring[5:19]
                return int(reply, 2)

if __name__ == '__main__':
        spi = MCP3208(0)

        count = 0
        a0 = 0
        a1 = 0
        a2 = 0
        a3 = 0

        while True:
                count += 1
                a0 += spi.read(0)
                a1 += spi.read(1)
                a2 += spi.read(2)
                a3 += spi.read(3)

                if count == 10:
                        print "ch0=%04d, ch1=%04d, ch2=%04d, ch3=%04d" % (a0/10, a1/10, a2/10, a3/10)
                        count = 0
                        a0 = 0
                        a1 = 0
                        a2 = 0
                        a3 = 0

