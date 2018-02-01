#!/usr/bin/python
import os, time
import usb.core
import usb.util
import pygtk
pygtk.require('2.0')
import gtk
from sys import exit
import math

# DYMO M25
VENDOR_ID = 0x0922
PRODUCT_ID = 0x8004

# USPS 75lb scale (doesn't work yet...)
#VENDOR_ID = 0x04d9
#PRODUCT_ID = 0x8010

# find the USB device
dev = usb.core.find(idVendor=VENDOR_ID,
                       idProduct=PRODUCT_ID)

def main():
    try:
        # was it found?
        if dev is None:
            print "device not found"
            exit()
        else:
            devmanufacturer = usb.util.get_string(dev, 256, 1)
            devname = usb.util.get_string(dev, 256, 2)
            print "device found: " + devmanufacturer + " " + devname

            interface = 0
            if dev.is_kernel_driver_active(interface) is True:
                print "but we need to detach kernel driver"
                dev.detach_kernel_driver(interface)

                # use the first/default configuration
                dev.set_configuration()
                print "claiming device"
                usb.util.claim_interface(dev, interface)

                # XXX would be good to release it when we're done:
                # 
                # print "release claimed interface"
                # usb.util.release_interface(dev, interface)
                # print "now attaching the kernel driver again"
                # dev.attach_kernel_driver(interface)
                # print "all done"

            listen()

    except KeyboardInterrupt as e: 
        print "\nquitting"
        exit();


def grab():
    try:
        # first endpoint
        endpoint = dev[0][(0,0)][0]

        # read a data packet
        attempts = 10
        data = None
        while data is None and attempts > 0:
            try:
                data = dev.read(endpoint.bEndpointAddress,
                                   endpoint.wMaxPacketSize)
            except usb.core.USBError as e:
                data = None
                if e.args == ('Operation timed out',):
                    attempts -= 1
                    print "timed out... trying again"
                    continue

        return data
    except usb.core.USBError as e:
        print "USBError: " + str(e.args)
    except IndexError as e:
        print "IndexError: " + str(e.args)


def listen():
    DATA_MODE_GRAMS = 2
    DATA_MODE_OUNCES = 11

    last_raw_weight = 0
    last_raw_weight_stable = 4

    print "listening for weight..."

    while True:
        time.sleep(.5)

        weight = 0
        print_weight = ""

        data = grab()
        if data != None:
            raw_weight = data[4] + data[5] * 256

        # +/- 2g
        if raw_weight > 0 and abs(raw_weight-last_raw_weight) > 0 and raw_weight != last_raw_weight:
            last_raw_weight_stable = 4
            last_raw_weight = raw_weight

        if raw_weight > 0 and last_raw_weight_stable >= 0:
            last_raw_weight_stable -= 1

        if raw_weight > 0 and last_raw_weight_stable == 0:
            if data[2] == DATA_MODE_OUNCES:
                ounces = raw_weight * 0.1
                weight = math.ceil(ounces)
                print_weight = "%s oz" % ounces
            elif data[2] == DATA_MODE_GRAMS:
                grams = raw_weight
                weight = math.ceil(grams)
                print_weight = "%s g" % grams

            print "stable weight: " + print_weight

            clipboard = gtk.clipboard_get()
            clipboard.set_text(str(weight))
            clipboard.store()


def probe():
    for cfg in dev:
        print "cfg: " + str(cfg.bConfigurationValue)
        print "descriptor: " + str(usb.util.find_descriptor(cfg, find_all=True, bInterfaceNumber=1))
        for intf in cfg:
            print "interfacenumber, alternatesetting: " + str(intf.bInterfaceNumber) + ',' + str(intf.bAlternateSetting)
            for ep in intf:
                print "endpointaddress: " + str(ep.bEndpointAddress)


#probe()
main()