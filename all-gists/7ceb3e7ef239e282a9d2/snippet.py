#!/usr/bin/env python
from __future__ import print_function

from datetime import datetime
from subprocess import call


from mercury206 import commands, communications, config


def update_rrd(path, values):
    value = ':'.join(['N'] + map(str, values))
    call(['rrdtool', 'update', path, value])
    print("Updated", path)


def add_readings(port, address):
    readings = commands.display_readings(port, address)
    update_rrd('tariffs.rrd', readings[:2])


def add_vcp(port, address):
    voltage, current, power = commands.instant_vcp(port, address)
    update_rrd('pcv.rrd', [power, current, voltage])


def main():
    settings = config.get_settings()
    port = communications.open_serial(settings['device'])
    now = datetime.now()
    if now.minute % 5 == 0:
        add_readings(port, settings['address'])
    add_vcp(port, settings['address'])


if __name__ == '__main__':
    main()