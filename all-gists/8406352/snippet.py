#!/usr/bin/python

# based on monitor-bluetooth
# Changes by Domen Puncer <domen@cba.si>

import gobject
import dbus
import dbus.mainloop.glib
import os



def property_changed(name, value, path, interface):
    iface = interface[interface.rfind(".") + 1:]
    val = str(value)
    print "{%s.PropertyChanged} [%s] %s = %s" % (iface, path, name, val)
    
    # we want this event: {Control.PropertyChanged} [/org/bluez/16797/hci0/dev_00_24_7E_51_F7_52] Connected = true
    # and when that happens: pactl load-module module-loopback source=bluez_source.00_24_7E_51_F7_52
    if iface == "Control" and name == "Connected" and val == "1":
        bt_addr = "_".join(path.split('/')[-1].split('_')[1:])
        cmd = "pactl load-module module-loopback source=bluez_source.%s" % bt_addr
        os.system(cmd)
        
    # here we want this event: {Control.PropertyChanged} [/org/bluez/16797/hci0/dev_00_24_7E_51_F7_52] Connected = false
    # and when that happens, we unload all loopback modules whose source is our bluetooth device
    elif iface == "Control" and name == "Connected" and val == "0":
        bt_addr = "_".join(path.split('/')[-1].split('_')[1:])
        cmd = "for i in $(pactl list short modules | grep module-loopback | grep source=bluez_source.%s | cut -f 1); do pactl unload-module $i; done" % bt_addr
        os.system(cmd)


def object_signal(value, path, interface, member):
    iface = interface[interface.rfind(".") + 1:]
    val = str(value)
    print "{%s.%s} [%s] Path = %s" % (iface, member, path, val)

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    bus.add_signal_receiver(property_changed, bus_name="org.bluez", signal_name = "PropertyChanged", path_keyword="path", interface_keyword="interface")

    mainloop = gobject.MainLoop()
    mainloop.run()