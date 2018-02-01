#!/usr/bin/python3
from __future__ import print_function
import argparse
import binascii
import os
import sys
from bluepy import btle
import paho.mqtt.client as mqtt

MISCALE_MAC = '88:0f:XX:XX:XX:XX'
MQTT_USERNAME = ''
MQTT_PASSWORD = ''
MQTT_HOST = '192.168.XXX.XXX'
MQTT_PORT = 1883
MQTT_TIMEOUT = 60

if os.getenv('C', '1') == '0':
    ANSI_RED = ''
    ANSI_GREEN = ''
    ANSI_YELLOW = ''
    ANSI_CYAN = ''
    ANSI_WHITE = ''
    ANSI_OFF = ''
else:
    ANSI_CSI = "\033["
    ANSI_RED = ANSI_CSI + '31m'
    ANSI_GREEN = ANSI_CSI + '32m'
    ANSI_YELLOW = ANSI_CSI + '33m'
    ANSI_CYAN = ANSI_CSI + '36m'
    ANSI_WHITE = ANSI_CSI + '37m'
    ANSI_OFF = ANSI_CSI + '0m'


class ScanProcessor():

    def __init__(self):
        self.mqtt_client = None
        self.connected = False
        self._start_client()

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if dev.addr == MISCALE_MAC.lower() and isNewDev:
            print ('    Device: %s (%s), %d dBm %s. ' %
                   (
                       ANSI_WHITE + dev.addr + ANSI_OFF,
                       dev.addrType,
                       dev.rssi,
                       ('' if dev.connectable else '(not connectable)'))
                   , end='')
            for (sdid, desc, data) in dev.getScanData():
                if data.startswith('1d18') and sdid == 22:
                    measunit = data[4:6]
                    measured = int((data[8:10] + data[6:8]), 16) * 0.01
                    unit = ''

                    if measunit.startswith(('03', 'b3')): unit = 'lbs'
                    if measunit.startswith(('12', 'b2')): unit = 'jin'
                    if measunit.startswith(('22', 'a2')): unit = 'kg' ; measured = measured / 2

                    if unit:
                        print('')
                        self._publish(round(measured, 2), unit)
                    else:
                        print("Scale is sleeping.")

            if not dev.scanData:
                print ('\t(no data)')
            print

    def _start_client(self):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        def _on_connect(client, _, flags, return_code):
            self.connected = True
            print("MQTT connection returned result: %s" % mqtt.connack_string(return_code))

        self.mqtt_client.on_connect = _on_connect

        self.mqtt_client.connect(MQTT_HOST, MQTT_PORT, MQTT_TIMEOUT)
        self.mqtt_client.loop_start()

    def _publish(self, weight, unit):
        if not self.connected:
            raise Exception('not connected to MQTT server')
        prefix = '{}/{}'.format('miscale/weight', unit)
        self.mqtt_client.publish(prefix, weight, qos=1, retain=True)
        print('\tSent data to topic %s: %s %s' % (prefix, weight, unit))


def main():

    scanner = btle.Scanner().withDelegate(ScanProcessor())

    print (ANSI_RED + "Scanning for devices..." + ANSI_OFF)
    devices = scanner.scan(5)

if __name__ == "__main__":
    main()
