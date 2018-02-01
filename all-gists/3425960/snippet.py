#!/usr/bin/env python
"""
OSX ONLY!

Monitor OSX application usage from your shell
and at the end of the day see how much you don't
work ;)

Author: Glen Zangirolami
http://theglenbot.com
http://codrspace.com/glenbot
http://twitter.com/glenbot

Usage:
./monitor_apps.py

When your ready to calculate times just
control+c to kill the script and it will print
the output
"""
import time
import datetime
from AppKit import NSWorkspace


class Application(object):
    def __init__(self, name):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.total_time = 0

    def timer_started(self):
        if self.start_time:
            return True
        return False

    def start_timer(self):
        self.start_time = time.time()

    def stop_timer(self):
        self.end_time = time.time()
        if self.start_time:
            self.append_time()

    def append_time(self):
        elapse_seconds = self.end_time - self.start_time
        self.total_time += elapse_seconds
        self.start_time = None
        self.end_time = None

    def elapse_time(self):
        return str(datetime.timedelta(seconds=self.total_time))

    def __str__(self):
        return self.name


class Applications(object):
    def __init__(self):
        self.registered_apps = {}
        self.current_app = None

    def is_current_app(self, app_name):
        return app_name is self.current_app

    def get_app(self, app_name):
        self.current_app = app_name
        if app_name in self.registered_apps:
            return self.registered_apps[app_name]
        return None

    def register(self, app_name):
        self.registered_apps[app_name] = Application(app_name)
        return self.get_app(app_name)

    def is_registered(self, app_name):
        return app_name in self.registered_apps.keys()

    def __iter__(self):
        sorted_apps = sorted(
            self.registered_apps.values(),
            key=lambda a: a.total_time,
            reverse=True
        )
        return iter(sorted_apps)


apps = Applications()

try:
    while True:
        active_application = NSWorkspace.sharedWorkspace().activeApplication()

        if active_application:
                app_name = active_application['NSApplicationName']

                # stop the timer on app change
                if not apps.is_current_app(app_name) and apps.current_app is not None:
                    apps.get_app(apps.current_app).stop_timer()

                # check if the app doesn't exist yet
                if not apps.is_registered(app_name):
                    app = apps.register(app_name)
                else:
                    app = apps.get_app(app_name)

                # start the timer
                if not app.timer_started():
                    app.start_timer()

                time.sleep(.2)

except KeyboardInterrupt:
    longest_name = max([len(app.name) for app in apps] + [len('Application')]) + 2
    print ''
    print "%s | %s" % ('Application'.ljust(longest_name), 'Total Time')
    print "-" * (longest_name + 18)
    for app in apps:
        print "%s | %s" % (
            app.name.ljust(longest_name),
            app.elapse_time(),
        )
