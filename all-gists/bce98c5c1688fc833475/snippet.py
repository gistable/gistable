#!/usr/bin/env python
# -*- coding: utf-8 -*-

# install dependencies:
# apt-get install libow-dev
# pip install onewire influxdb

import argparse
from datetime import datetime
import logging
import signal
import sys
from threading import Timer
from time import time

from onewire import Onewire
from influxdb import client as influxdb


def int_signal_handler(signal, frame):
    logging.info("interrupt detected")
    sys.exit(0)

signal.signal(signal.SIGINT, int_signal_handler)


class ServiceLocation(object):

    def __init__(self, hostname, port=None):
        self.hostname = hostname
        self.port = port


class ServiceLocationAction(argparse.Action):

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None and nargs != 1:
            raise ValueError("Only one argument is allowed for a service location.")
        super(ServiceLocationAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if ":" in values:
            hostname, port = values.split(":", 1)
            port = int(port)
            setattr(namespace, self.dest, ServiceLocation(hostname, port))
        else:
            hostname = values
            setattr(namespace, self.dest, ServiceLocation(hostname))


class InfluxDatabaseWriter(object):

    def __init__(self, location, name):
        self._client = influxdb.InfluxDBClient(location.hostname, location.port)
        self._client.switch_database(name)

    def write(self, datum):
        self._client.write_points([{
            "measurement": datum.measurement,
            "tags": {},
            "time": datum.time.isoformat(),
            "fields": {"value": datum.value}}])


class OneWireTemperatureSensor(object):

    def __init__(self, location, identifier):
        ow = Onewire("{hostname:s}:{port:d}".format(
            hostname=location.hostname, port=location.port))
        self._sensor = ow.sensor(identifier)

    @property
    def type(self):
        return self._sensor.sensor_type

    @property
    def identifier(self):
        return self._sensor.path

    @property
    def temperature(self):
        temperature = self._sensor.read("temperature")
        if temperature:
            return float(temperature)
        else:
            return None


class TimeSeriesDatum(object):

    def __init__(self, measurement, value):
        self.time = datetime.utcnow()
        self.measurement = measurement
        self.value = value


class Repeater(object):

    def __init__(self, interval, function, *args):
        self._interval = interval
        self._function = function
        self._arguments = args

    def __call__(self):
        self._start_timer()
        self._call_function()

    def _call_function(self):
        self._function(*self._arguments)

    def _start_timer(self):
        # align the execution of the function with the next multiple of
        # the delay interval from the original start time
        interval = self._interval
        start_seconds = self._start_seconds
        delay_seconds = interval - ((time() - start_seconds) % interval)
        Timer(delay_seconds, self).start()

    def start(self):
        self._start_seconds = time()
        self._start_timer()
        self._call_function()


def read_temperature(sensor, database):
    temperature = sensor.temperature
    if temperature is not None:
        datum = TimeSeriesDatum("temp", temperature)
        database.write(datum)
        logging.info("temperature is {value:f} °C [{time!s}]".format(
            value=datum.value, time=datum.time))
    else:
        logging.warning("could not convert temperature \"{value:s}\"".format(
            value=temperature))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="read temperatures from a OneWire sensor")
    parser.add_argument("device", type=str, help="device ID")
    parser.add_argument("-I", "--influx", type=str, default="localhost",
                        help="InfluxDB hostname (default: %(default)s",
                        action=ServiceLocationAction),
    parser.add_argument("-D", "--database", type=str, default=None,
                        help="InfluxDB database name"),
    parser.add_argument("-H", "--host", type=str, default="localhost:4304",
                        help="owserver hostname (default: %(default)s)",
                        action=ServiceLocationAction),
    parser.add_argument("-d", "--delay", type=int, default=1,
                        help="delay between sensor readings in seconds (default: %(default)d)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    database = InfluxDatabaseWriter(args.influx, args.database)
    logging.info("connected to InfluxDB server at {hostname:s}:{port:d}".format(
        hostname=args.influx.hostname, port=args.influx.port))

    sensor = OneWireTemperatureSensor(args.host, args.device)
    logging.info("connected to OneWire server at {hostname:s}:{port:d}".format(
        hostname=args.host.hostname, port=args.host.port))
    logging.info("found device {identifier:s} (type = {type:s})".format(
        identifier=sensor.identifier, type=sensor.type))

    Repeater(args.delay, read_temperature, sensor, database).start()
