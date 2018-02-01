#!/usr/bin/env python
from gi.repository import Notify
import subprocess
from time import sleep, time
from sys import argv
import dbus


def send_notification(title, text):
    try:
        if Notify.init(argv[0]):
            n = Notify.Notification.new("Notify")
            n.update(title, text)
            n.set_urgency(2)
            if not n.show():
                raise SyntaxError("sending notification failed!")
        else:
            raise SyntaxError("can't initialize notification!")
    except SyntaxError as error:
        print(error)
        if error == "sending notification failed!":
            Notify.uninit()
    else:
        Notify.uninit()


def run_cmd(cmdlist):
    try:
        stdout = subprocess.check_output(cmdlist)
    except subprocess.CalledProcessError:
        pass
    else:
        if stdout:
            return stdout


def run_dbus_method(bus_type, obj, path, interface, method, arg):
    if bus_type == "session":
        bus = dbus.SessionBus()
    if bus_type == "system":
        bus = dbus.SystemBus()
    proxy = bus.get_object(obj, path)
    method = proxy.get_dbus_method(method, interface)
    if arg:
        return method(arg)
    else:
        return method()


def suspend_system():
    run_dbus_method('session',
                    'com.canonical.Unity',
                    '/com/canonical/Unity/Session',
                    'com.canonical.Unity.Session',
                    'Suspend', 'None')


def get_battery_percentage():
    output = run_cmd(['upower', '--dump']).decode().split('\n')
    found_battery = False
    for line in output:
        if 'BAT' in line:
            found_battery = True
        if found_battery and 'percentage' in line:
            return line.split()[1].split('%')[0]


def main():
    end = time()
    battery_path = ""
    for line in run_cmd(['upower', '-e']).decode().split('\n'):
        if 'battery_BAT' in line:
            battery_path = line
            break
    while True:
        notified = False
        while subprocess.call(['on_ac_power']) == 0:

            sleep(0.25)
            run_dbus_method('system', 'org.freedesktop.UPower',
                            battery_path, 'org.freedesktop.UPower.Device',
                            'Refresh', 'None')
            battery_percentage = int(get_battery_percentage())
            if battery_percentage == int(argv[2]) and not notified:
               subprocess.call( ['zenity', '--info','--text', 'Battery reached' + argv[2] + '%'  ]  ) 
               notified = True
        while subprocess.call(['on_ac_power']) == 1:

            sleep(0.25)
            run_dbus_method('system', 'org.freedesktop.UPower',
                            battery_path, 'org.freedesktop.UPower.Device',
                            'Refresh', 'None')
            battery_percentage = int(get_battery_percentage())
 
            if battery_percentage <= int(argv[1]):
                if battery_percentage <= 10:
                    send_notification('Low Battery',
                                      'Will suspend in 60 seconds')
                    sleep(60)
                    suspend_system()
                    continue
                if end < time():
                    end = time() + 600
                    send_notification('Low Battery', 'Plug in your charger')

if __name__ == '__main__':
    main()
