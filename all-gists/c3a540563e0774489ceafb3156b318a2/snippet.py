#!/usr/bin/env python
# vim:fileencoding=utf-8

""" [NAME] script or package easy description

[DESCRIPTION] script or package description
"""
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import subprocess
import threading
import shlex
import time
import os, sys, io
import signal
import re

__author__  = 'holly'
__version__ = '1.0'

DESCRIPTION = 'logmon.py / LogMonitor'

REPLACE_STRING    = "<%%%%>"
REPLACE_STRING_EX = "<%%%N>"
LOG_FORMAT        = "%(asctime)s %(name)s %(levelname)s: %(message)s"
ACTION_TIMEOUT    = 3
CONFIG_FILE       = "/etc/logmon/logmon.conf"
INTERVAL          = 0.2
VERBOSE           = False

class Config:

    def __init__(self, config_file=CONFIG_FILE):

        self._config_file = config_file
        self._config = {}
        self.parse()

    @property
    def config_file(self):
        return self._config_file

    @property
    def config(self):
        return self._config

    def parse(self, config_file=None):

        config = {}
        target_regex = re.compile(r"^:(.+)$")
        message_regex = re.compile(r"^(\(.+\))$")

        if config_file is None:
            config_file = self.config_file

        with open(config_file, "r") as f:
            target = ""
            message = ""
            for line in f:
                line = line.strip()
                if not line or len(line) == 0:
                    continue
                if line[0] == "#":
                    continue

                res = target_regex.match(line)
                if res:
                    target = res.group(1)
                    continue

                res = message_regex.match(line)
                if res:
                    message = res.group(0)
                    continue

                if len(target) == 0 or len(message) == 0:
                    continue

                if target not in config:
                    config.update({target: {}})
                if message not in config[target]:
                    config[target].update({message: []})
                config[target][message].append(line)

        self._config = config


class Tail:

    def __init__(self, event, interval=INTERVAL):

        self.f     = None
        self.pos   = None
        self.size  = None
        self.mtime = None

        self._interval = interval
        self._event = event
        self._first = True
        self._stop  = False

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, v):
        if isinstance(v, int):
            self._interval = float(v)
        elif isinstance(v, float):
            self._interval = v

    @property
    def event(self):
        return self._event

    @property
    def first(self):
        return self._first

    @first.setter
    def first(self, v):
        if v is True or v is False:
            self._first = v

    @property
    def stop(self):
        return self._stop

    @stop.setter
    def stop(self, v):
        if v is True or v is False:
            self._stop = v

    def stopped(self):
        if self.event.is_set() or self.stop is True:
            return True

    def fclose(self):
        self.stop = True
        if isinstance(self.f, io.TextIOWrapper) and self.f.closed is False:
            self.f.close()

    def tail_f(self, filename):

        while True:

            if self.stopped():
                break

            try:
                self.f = open(filename, "r")
                if self.first:
                    self.f.seek(0, 2)
                    self.first = False
                self.pos   = self.f.tell()
                self.size  = os.path.getsize(filename)
                self.mtime = os.stat(filename).st_mtime
            except FileNotFoundError as e:
                print("{0} is not exists. wait {1} sec....".format(filename, self.interval))
                time.sleep(self.interval)
            except PermissionError as e:
                print("{0} is not permited. end".format(filename))
                self.stop = True
            else:
                while True:
                    if self.stopped():
                        break
                    if not os.path.exists(self.f.name):
                        break

                    size  = os.path.getsize(self.f.name)
                    mtime = os.stat(self.f.name).st_mtime
                    if self.mtime < mtime and self.size >= size:
                        self.size = size
                        self.mtime = mtime
                        self.f.seek(0, 0)
                        self.pos   = self.f.tell()

                    line = self.f.readline()
                    if not line:
                        self.f.seek(self.pos)
                        time.sleep(self.interval)
                    else:
                        line = line.rstrip()
                        self.pos = self.f.tell()
                        yield line
            finally:
                self.fclose()

class Log():

    def __init__(self, log_file=None, quiet=False, debug=False):
        self._logger = logging.getLogger(__name__)

        self._logger.addHandler(logging.StreamHandler())
        if log_file:
            fh = logging.FileHandler(log_file)
            fh.formatter = logging.Formatter(fmt=LOG_FORMAT)
            self._logger.addHandler(fh)

        if quiet:
            self._logger.setLevel(logging.CRITICAL)
        elif debug:
            self._logger.setLevel(logging.DEBUG)
        else:
            self._logger.setLevel(logging.INFO)

    def shutdown(self):
        logging.shutdown()

    @property
    def logger(self):
        return self._logger


parser = ArgumentParser(description=DESCRIPTION)
parser.add_argument('--disable-shell-escape', action='store_true', default=False, help='enable escape command replace string (Default: True)')
parser.add_argument('--enable-regex-ignorecase', action='store_true', default=False, help='enable regex ignorecase (Default: False)')
parser.add_argument('--config-file', '-f', action='store', default=CONFIG_FILE, help='config file (Default: {0})'.format(CONFIG_FILE))
parser.add_argument('--log-file', '-l', action='store', help='output log file(Default: STDOUT)')
parser.add_argument('--check', '-c', action='store_true', help='check config')
parser.add_argument('--interval', '-i', action='store', default=INTERVAL, type=float, help='interval second (Default: {0} sec)'.format(INTERVAL))
parser.add_argument('--quiet', '-q', action='store_true', default=False, help='quiet mode')
parser.add_argument('--verbose', action='store_true', help='output verbose message')
parser.add_argument('--version', '-v', action='version', version='%(prog)s ' + __version__)
args = parser.parse_args()

config = Config(config_file=args.config_file)
log    = Log(log_file=args.log_file, quiet=args.quiet, debug=args.verbose)


def signal_handler(event, signum, frame):
    log.logger.info("signal {0} received.".format(signum))
    event.set()

def phoenix(event, executor, signum, frame):
    log.logger.info("signal {0} received.".format(signum))
    event.set()
    executor.shutdown()
    new_environ = os.environ.copy()
    args = [sys.executable, [sys.executable] + sys.argv, new_environ]
    log.logger.info('re-exec. shutdown current process')
    log.shutdown()
    os.execve(*args)

def check_config():
    print("Config file: {0}".format(config.config_file))

    for target in config.config:
        print()
        print("Logfile: {0}".format(target))
        for message in config.config[target]:
            print("  Message: {0}".format(message))
            for action in config.config[target][message]:
                 print("    Action: {0}".format(action))
    print()

def watch(event, target, config):
    message = list(config.keys())[0]
    actions = config[message]

    flags = re.I if args.enable_regex_ignorecase else 0
    regex = re.compile(r"{0}".format(message), flags=flags)

    log.logger.info("watch {0}".format(target))
    tail    = Tail(event, interval=args.interval)

    log.logger.debug("thread_id {0}: start thread.".format(threading.get_ident()))
    log.logger.debug("target:{0} message:{1}".format(target, message))
    for line in tail.tail_f(target):
        result = regex.search(line)
        if not result:
            continue
        log.logger.info("match line in {0}: {1}".format(target, line))
        if not args.disable_shell_escape:
            line = shlex.quote(line)
        for action in actions:
            action = action.replace(REPLACE_STRING, line)
            if len(result.groups()) > 0:
                i = 1
                for group in result.groups():
                    if not args.disable_shell_escape:
                        group = shlex.quote(group)
                    replace_string = REPLACE_STRING_EX.replace("N", str(i))
                    action = action.replace(replace_string, group)
                    i = i + 1

            log.logger.info("action: {0}".format(action))
            subprocess.call(action, shell=True, timeout=ACTION_TIMEOUT)

    log.logger.debug("thread_id {0}: break thread.".format(threading.get_ident()))

def main():
    """ [FUNCTIONS] method or functon description
    """

    executor = None
    event = threading.Event()

    log.logger.info("start Logmonitor")

    for i in signal.SIGINT, signal.SIGUSR1, signal.SIGTERM:
        signal.signal(i, lambda signum, frame: signal_handler(event, signum, frame))
    signal.signal(signal.SIGHUP, lambda signum, frame: phoenix(event, executor, signum, frame))

    if args.check:
        check_config()
        return

    executor = ThreadPoolExecutor(max_workers=len(config.config)) 
    future_to_targets = { executor.submit(watch, event, target, config.config[target]): target for target in config.config }
    for future in as_completed(future_to_targets):
        target = future_to_targets[future]
        try:
            data = future.result()
        except Exception as exc:
            log.logger.critical('%s generated an exception: %s' % (target, exc))
        else:
            pass
    executor.shutdown()

    log.logger.info("end Logmonitor")
    sys.exit(0)

if __name__ == "__main__":
    main()

