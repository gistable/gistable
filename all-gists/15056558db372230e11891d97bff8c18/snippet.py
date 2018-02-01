#!/usr/bin/env python

from collections import namedtuple
import ctypes
import datetime
import fcntl
import imaplib
import json
import multiprocessing
import os
import re
import socket
import struct
import subprocess
import sys
import threading
import time
import urllib
import urllib2

VALUE_GOOD = 'good'
VALUE_NEUTRAL = 'neutral'
VALUE_BAD = 'bad'
VALUE_URGENT = 'urgent'

libc = ctypes.CDLL('libc.so.6')
flush_resolver_cache = getattr(libc, '__res_init')

class Configuration(object):
    colors_re = re.compile('.*?color([\d]+):\s*?(#[A-Fa-f0-9]+)')

    def __init__(self):
        # Defaults.
        self.config = {
            # Mickey.
            'interval': 5,
            'socket_timeout': 10,

            # Formatter config.
            'formatter': 'bar',
            'bar_size': 7,
            'bar_full': '#',
            'bar_empty': ' ',
            'bar_framing': '[%s]',

            # Module list.
            'modules': [
                #'email',
                'weather',
                'cpu',
                'ram',
                'disk',
                'battery',
                'ip',
                'loadavg',
                'clock',
            ],

            # Module config.
            'weather_query': 'Lawrence,KS',
            'weather_units': 'imperial',
            'ip_interfaces': ['wlan0', 'eth0'],
            'clock_format': '%Y-%m-%d %H:%M:%S',
            'clock_calendar_url': (
                'https://www.google.com/calendar/render?tab=mc'),

            # Templates.
            # 'template_<module_name>': '...',

            # Colors.
            # 'color_<module_name>': '...',
            'colors': {},
            'color_weather': 1,
            'color_cpu': 2,
            'color_ram': 4,
            'color_disk': 3,
            'color_battery': 13,
            'color_ip': 2,
            'color_loadavg': 2,
            'color_clock': 11,
        }

    def load(self):
        colors = self.read_colors()
        colors[VALUE_GOOD] = colors.get(10, '#00dd00')
        colors[VALUE_NEUTRAL] = colors.get(7, '#cccccc')
        colors[VALUE_BAD] = colors.get(9, '#dd0000')
        colors[VALUE_URGENT] = '#ffff00'

        self.config['colors'].update(colors)
        config_data = self.read_config_file()
        if config_data:
            self.config.update(self.parse_config(config_data))

    def read_colors(self):
        # Query X server resource database for terminal colors.
        try:
            xrdb = subprocess.Popen(['xrdb', '-q'], stdout=subprocess.PIPE)
            out, _ = xrdb.communicate()
        except OSError:
            return {}
        return dict(
            (int(idx), val) for idx, val in self.colors_re.findall(out))

    def read_config_file(self):
        config_home = (os.environ.get('XDG_CONFIG_HOME') or
                       os.path.join(os.environ['HOME'], '.config'))
        config_file = os.path.join(config_home, 'mickey.conf')
        if os.path.exists(config_file):
            with open(config_file) as fh:
                return fh.read()

    def parse_config(self, raw_config):
        config = {}
        for line in raw_config.splitlines():
            if '=' in line:
                key, value = [s.strip() for s in line.split('=', 1)]
                if value.isdigit():
                    value = int(value)
                elif ',' in value:
                    value = [s.strip() for s in value.split(',') if s.strip()]
                config[key] = value
        return config

FORMATTERS = {}
MODULES = {}

def registered_metaclass(registry):
    class _RegisteredBase(type):
        def __new__(cls, name, bases, attrs):
            obj = super(_RegisteredBase, cls).__new__(cls, name, bases, attrs)
            if attrs.get('name'):
                registry[attrs['name']] = obj
            return obj
    return _RegisteredBase

class BaseFormatter(object):
    __metaclass__ = registered_metaclass(FORMATTERS)

    # Required attributes.
    name = None

    def __init__(self, config):
        self.config = config

    def format_value(self, value):
        return value

class Formatter(BaseFormatter):
    name = 'default'

class BarFormatter(BaseFormatter):
    name = 'bar'

    def __init__(self, config):
        super(BarFormatter, self).__init__(config)
        self.bars = config.get('bar_size', 10)
        self.full = config.get('bar_full', '#')
        self.empty = config.get('bar_empty', ' ')
        self.framing = config.get('bar_framing', ['%s'])

    def format_value(self, value):
        num_bars = int(round(self.bars * value))
        value = (self.full * num_bars) + (self.empty * (self.bars - num_bars))
        if self.framing:
            value = self.framing % value
        return value

class Module(object):
    __metaclass__ = registered_metaclass(MODULES)
    __counter = 0
    __instance_id = 0

    # Required attributes.
    name = None
    template = '%(formatted_value)s'

    # Optional attributes.
    cache_timeout = None
    _cached_value = None
    _delay = 1.
    _stale_steps = 20
    _stale_time = None

    def __init__(self, config):
        Module.__counter += 1
        self.__instance_id = Module.__counter
        self.config = config
        if self.cache_timeout:
            self._backoff = self.cache_timeout ** (1. / self._stale_steps)
        self.template = self.config.get(
            'template_%s' % self.name, self.template)
        self.post_init()

    def is_enabled(self):
        return True

    def post_init(self):
        pass

    def get_value(self):
        raise NotImplementedError

    def get_value_type(self, value):
        return VALUE_NEUTRAL

    def get_color(self, value):
        custom_color_key = 'color_%s' % self.name
        value_type = self.get_value_type(value)
        if value_type != VALUE_NEUTRAL:
            custom_color_key += '_%s' % value_type
        if custom_color_key in self.config:
            color_value = self.config[custom_color_key]
        else:
            color_value = value_type
        return self.config['colors'][color_value]

    def get_instance(self):
        return '%s_%s' % (self.name, self.__instance_id)

    def is_stale(self):
        return self._stale_time >= time.time()

    def value(self):
        if self.cache_timeout is None:
            return self.get_value()
        # Handle caching logic. If the stale time is in the past, attempt to
        # re-calculate the value.
        if self._stale_time < time.time():
            try:
                self._cached_value = self.get_value()
            except Exception as exc:
                self._delay *= self._backoff
                if self._delay > self.cache_timeout:
                    self._delay = self.cache_timeout
                self._stale_time = time.time() + self._delay
                self._cached_value = exc.message
            else:
                self._delay = 1.
                self._stale_time = time.time() + self.cache_timeout
        return self._cached_value

    def on_click(self, data):
        pass

    def render(self, data):
        return self.template % data

    def run_command(self, *args):
        subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    def open_url(self, url):
        self.run_command('xdg-open', url)

class CPU(Module):
    name = 'cpu'
    template = 'C %(formatted_value)s'
    prev_idle = 0
    prev_total = 0

    def read_proc_stat(self):
        total = idle = 0
        with open('/proc/stat') as fh:
            contents = fh.readlines()
        for line in contents:
            parts = line.split()
            if parts[0] == 'cpu':
                for i in range(1, len(parts)):
                    val = int(parts[i])
                    total += val
                    if i == 4:
                        idle = val
                break

        return total, idle

    def get_value(self):
        total, idle = self.read_proc_stat()

        if self.prev_idle > 0:
            idle_ticks = idle - self.prev_idle
            total_ticks = total - self.prev_total
            cpu_usage = (total_ticks - idle_ticks) / float(total_ticks)
        else:
            cpu_usage = 0

        self.prev_idle = idle
        self.prev_total = total

        return cpu_usage

    def get_value_type(self, value):
        if value > .8:
            return VALUE_BAD
        return VALUE_NEUTRAL

    def on_click(self, data):
        self.run_command('urxvt', '-e', 'htop')

class Disk(Module):
    cache_timeout = 60
    name = 'disk'
    template = 'D %(formatted_value)s'

    def post_init(self):
        self.path = self.config.get('disk_path', '/')

    def get_value(self):
        res = os.statvfs(self.path)
        free = res.f_bfree * res.f_bsize
        total = res.f_blocks * res.f_bsize
        return float(free) / total

    def get_value_type(self, value):
        if value < .02:
            return VALUE_URGENT
        elif value < .1:
            return VALUE_BAD
        return VALUE_NEUTRAL

class RAM(Module):
    name = 'ram'
    template = 'R %(formatted_value)s'

    def get_value(self):
        with open('/proc/meminfo') as fh:
            content = fh.readlines()
        free = total = 0
        for line in content:
            key, value = line.split(':', 1)
            if key == 'MemTotal':
                total = int(value.split()[0])
            elif key in ('MemFree', 'Buffers', 'Cached'):
                free += int(value.split()[0])
        return float(total - free) / total

    def get_value_type(self, value):
        if value > .9:
            return VALUE_URGENT
        elif value > .7:
            return VALUE_BAD
        return VALUE_NEUTRAL

class LoadAvg(Module):
    name = 'loadavg'

    def post_init(self):
        self._cores = multiprocessing.cpu_count()

    def get_value(self):
        self._loadavg = os.getloadavg()
        return '%.02f %.02f %.02f' % self._loadavg

    def get_value_type(self, value):
        if self._loadavg[0] > self._cores:
            return VALUE_BAD
        return VALUE_NEUTRAL

class IPAddress(Module):
    cache_timeout = 300
    name = 'ip'
    SIOCGIFADDR = 0x8915

    def get_value(self):
        # http://stackoverflow.com/a/9267833/254346
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockfd = sock.fileno()
        for iface in self.config.get('ip_interfaces') or ['wlan0']:
            ifreq = struct.pack('16sH14s', iface, socket.AF_INET, '\x00' * 14)
            try:
                res = fcntl.ioctl(sockfd, self.SIOCGIFADDR, ifreq)
            except:
                continue
            ip = struct.unpack('16sH2x4s8x', res)[2]
            return socket.inet_ntoa(ip)
        return 'Unknown'

    def get_value_type(self, value):
        if value == 'Unknown':
            return VALUE_BAD
        return VALUE_NEUTRAL

class Clock(Module):
    name = 'clock'

    def post_init(self):
        self._format = self.config.get('clock_format') or '%Y-%m-%d %H:%M:%S'

    def get_value(self):
        return datetime.datetime.now().strftime(self._format)

    def on_click(self, data):
        self.open_url(self.config['clock_calendar_url'])

class Battery(Module):
    cache_timeout = 60
    name = 'battery'

    DISCHARGING = 'BAT'
    CHARGING = 'CHR'
    FULL = 'FULL'

    Status = namedtuple('Status', (
        'status', 'percent_remaining', 'seconds_remaining', 'consumption'))

    def post_init(self):
        self.battery = '0'

    def read_battery(self):
        with open('/sys/class/power_supply/BAT%s/uevent' % self.battery) as fh:
            content = fh.readlines()
        data = dict(line.strip().split('=', 1) for line in content)
        remaining = present_rate = voltage = full_design = 0.0
        in_watts = False
        status = self.DISCHARGING

        if data.get('POWER_SUPPLY_STATUS') == 'Charging':
            status = self.CHARGING
        elif data.get('POWER_SUPPLY_STATUS') == 'Full':
            status = self.FULL

        def first_float(*keys):
            for key in keys:
                if key in data:
                    return float(data[key])
            return 0.
        remaining = first_float('POWER_SUPPLY_ENERGY_NOW',
                                'POWER_SUPPLY_CHARGE_NOW')
        present_rate = first_float('POWER_SUPPLY_CURRENT_NOW',
                                   'POWER_SUPPLY_POWER_NOW')
        voltage = first_float('POWER_SUPPLY_VOLTAGE_NOW')
        full_design = first_float('POWER_SUPPLY_CHARGE_FULL_DESIGN',
                                  'POWER_SUPPLY_ENERGY_FULL_DESIGN')
        in_watts = 'POWER_SUPPLY_ENERGY_NOW' in data

        if not in_watts:
            present_rate = (voltage / 1000) * (present_rate / 1000)
            remaining = (voltage / 1000) * (remaining / 1000)
            full_design = (voltage / 1000) * (full_design / 1000)

        if full_design == 0.:
            return Status('ERR', 0, 0, 0)

        percent_remaining = remaining / full_design
        seconds_remaining = 0
        if present_rate > 0:
            if status == self.CHARGING:
                remaining_time = (full_design - remaining) / present_rate
            elif status == self.DISCHARGING:
                remaining_time = remaining / present_rate
            seconds_remaining = remaining_time * 3600

        consumption = present_rate / 1000000
        return self.Status(
            status,
            percent_remaining,
            seconds_remaining,
            consumption)

    def get_value(self):
        self._status = self.read_battery()
        return self._status.percent_remaining

    def get_value_type(self, value):
        if value < .04:
            return VALUE_URGENT
        elif value < .15:
            return VALUE_BAD
        return VALUE_NEUTRAL

    def render(self, data):
        hours = self._status.seconds_remaining / 3600
        minutes = (self._status.seconds_remaining % 3600) / 60
        return '%s %s (%d:%02d %.1fW)' % (
            self._status.status,
            data['formatted_value'],
            hours,
            minutes,
            self._status.consumption)

class Weather(Module):
    cache_timeout = 1800
    name = 'weather'
    current_endpoint = 'http://api.openweathermap.org/data/2.5/weather'
    forecast_endpoint = 'http://api.openweathermap.org/data/2.5/forecast/daily'

    def post_init(self):
        query = self.config.get('weather_query') or 'Lawrence,KS'
        units = self.config.get('weather_units') or 'imperial'
        self._current_url = '%s?%s' % (
            self.current_endpoint,
            urllib.urlencode({'q': query, 'units': units}))
        self._forecast_url = '%s?%s' % (
            self.forecast_endpoint,
            urllib.urlencode({'q': query, 'units': units, 'cnt': 2}))

    def fetch(self, url):
        try:
            fh = urllib2.urlopen(url)
            return json.loads(fh.read())
        except:
            pass

    def format_forecast(self, data):
        return '%s %s/%s' % (
            data['weather'][0]['main'],
            int(data['temp']['max']),
            int(data['temp']['min']))

    def get_value(self):
        current_data = self.fetch(self._current_url)
        forecast_data = self.fetch(self._forecast_url)

        if not current_data or not forecast_data:
            flush_resolver_cache(None)
            raise ValueError('<disconnected>')

        current = int(current_data['main']['temp'])
        return '%s: %s' % (
            current,
            self.format_forecast(forecast_data['list'][0]))

    def on_click(self, data):
        self.open_url('http://www.wunderground.com/cgi-bin/findweather/'
                      'getForecast?query=%s' % self.config['weather_query'])

class EmailHandler(Module):
    cache_timeout = 120
    _stale_steps = 2  # Reach stale really quickly.
    name = 'email'

    def post_init(self):
        self.host = self.config.get('email_host')
        self.port = self.config.get('email_port') or 993
        self.username = self.config.get('email_username')
        self.password = self.config.get('email_password')
        self._message_ids = []

    def is_enabled(self):
        return all([self.host, self.port, self.username, self.password])

    def get_value(self):
        try:
            imap = imaplib.IMAP4_SSL(self.host, str(self.port))
        except:
            flush_resolver_cache(None)
            raise ValueError('<connect fail>')
        try:
            imap.login(self.username, self.password)
        except:
            raise ValueError('<auth fail>')
        try:
            imap.select()
            res, msg_ids = imap.search(None, 'UnSeen')
        except:
            raise ValueError('<inbox fail>')
        self._message_ids = [msg_id for msg_id in msg_ids[0].split() if msg_id]
        return 'Inbox: %s' % len(self._message_ids)

    def get_value_type(self, value):
        if len(self._message_ids) > 10:
            return VALUE_URGENT
        return VALUE_NEUTRAL

    def on_click(self, data):
        self.open_url('https://mail.google.com/mail/u/0/?ui=2&shva=1#inbox')


class EventHandler(threading.Thread):
    def __init__(self, config, modules):
        self.config = config
        self.modules = {module.get_instance(): module for module in modules}
        super(EventHandler, self).__init__()

    def run(self):
        while True:
            line = sys.stdin.readline().strip(',')
            try:
                data = json.loads(line)
            except ValueError:
                continue
            else:
                if data['instance'] in self.modules:
                    self.modules[data['instance']].on_click(data)

class Mickey(object):
    def __init__(self, default_formatter=None):
        self.config = self.load_config()
        self._formatter = default_formatter or self.get_default_formatter()
        self._modules = self.load_modules()
        self._events_t = EventHandler(self.config, self._modules)
        self._events_t.daemon = True
        socket.setdefaulttimeout(self.config['socket_timeout'])

    def get_default_formatter(self):
        formatter = FORMATTERS[self.config.get('formatter', 'default')]
        return formatter(self.config)

    def load_config(self):
        config = Configuration()
        config.load()
        return config.config

    def load_modules(self):
        modules = [
            MODULES[module_name](self.config)
            for module_name in self.config['modules']
            if module_name in MODULES]
        return filter(lambda m: m.is_enabled(), modules)

    def get_module_data(self, module):
        value = module.value()
        if type(value) in (float, int, long):
            try:
                formatted = self._formatter.format_value(value)
            except:
                formatted = '<error formatting>'
        else:
            formatted = value

        data = {
            'value': value,
            'formatted_value': formatted,
            'name': module.name,
        }
        return {
            'color': module.get_color(value),
            'instance': module.get_instance(),
            'name': module.name,
            'full_text': module.render(data),
        }

    def write(self, data):
        sys.__stdout__.write('%s\n' % data)
        sys.__stdout__.flush()

    def run_loop(self):
        self._events_t.start()
        self.write('{"version":1,"click_events":true}')
        self.write('[')
        while True:
            module_data = [
                self.get_module_data(module) for module in self._modules]
            self.write('%s,' % json.dumps(module_data))
            time.sleep(self.config['interval'])

if __name__ == '__main__':
    Mickey().run_loop()
