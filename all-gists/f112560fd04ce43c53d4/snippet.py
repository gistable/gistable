"""
Data types for the observation report types.

:author: Martin Norbury (martin.norbury@gmail.com)
"""
from xml.etree import ElementTree
from collections import defaultdict

from dateutil.parser import parse as datetime_parser


def read_report_from_file(filename):
    with open(filename) as fsock:
        return read_report_from_string(fsock.read())


def read_report_from_string(report_string):
    xml_root = ElementTree.fromstring(report_string)
    return Report(xml_root)


class Report(object):
    def __init__(self, xml):
        self._xml = xml

    @property
    def id(self):
        return self._xml.get('id')

    @property
    def type(self):
        return self._xml.get('type')

    @property
    def start(self):
        return datetime_parser(self._xml.find('start').text, ignoretz=True)

    @property
    def end(self):
        return datetime_parser(self._xml.find('end').text, ignoretz=True)

    @property
    def state(self):
        return self._xml.find('state').text

    @property
    def resource(self):
        return self._xml.find('resource').text

    @property
    def events(self):
        return [Event(x) for x in self._xml.findall('event')]

    @property
    def events_by_type(self):
        events_by_type = defaultdict(lambda: [])
        for event in self.events:
            events_by_type[event.command].append(event)
        return events_by_type

    def duration(self):
        return self.end - self.start

    def command_start_time(self, command, relative=False):
        events_for_command = self.events_by_type[command]
        command_start_time = events_for_command[0].time
        return command_start_time - self.start if relative else command_start_time


class Event(object):
    def __init__(self, xml):
        self._xml = xml

    @property
    def command(self):
        return self._xml.get('command')

    @property
    def time(self):
        return datetime_parser(self._xml.find('time').text, ignoretz=True)

    @property
    def state(self):
        return self._xml.find('state').text

    def __repr__(self):
        return "{0} {1} {2}".format(self.command, self.time, self.state)