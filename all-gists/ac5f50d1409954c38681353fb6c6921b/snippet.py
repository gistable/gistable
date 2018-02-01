#!/usr/bin/env python
import dbus
import dbus.service

class FakeScreenSaver(dbus.service.Object):
    def __init__(self):
        self.session_bus = dbus.SessionBus()
        name = dbus.service.BusName('org.freedesktop.ScreenSaver', bus=self.session_bus)
        dbus.service.Object.__init__(self, name, '/org/freedesktop/ScreenSaver')

    @dbus.service.method('org.freedesktop.ScreenSaver', in_signature='ss', out_signature='u')
    def Inhibit(self, application_name, reason_for_inhibit):
        print('Inhibit request by "' + application_name + '" because of "' + reason_for_inhibit + '"')
        return 1337
    
    @dbus.service.method('org.freedesktop.ScreenSaver', in_signature='u', out_signature='')
    def UnInhibit(self, cookie):
        print('UnInhibit request with cookie: ' + str(cookie))

if __name__ == '__main__':
    # using glib
    import dbus.mainloop.glib
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    import gobject
    loop = gobject.MainLoop()
    fake = FakeScreenSaver()
    loop.run()