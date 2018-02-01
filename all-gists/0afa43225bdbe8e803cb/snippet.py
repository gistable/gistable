from __future__ import print_function
import dbus
import sys
import dbus.service
import dbus.mainloop.glib
import gobject as gobject


dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()


BLUEZ_SERVICE_NAME = "org.bluez"
DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
DBUS_PROP_IFACE = "org.freedesktop.DBus.Properties"

GATT_SERVICE_IFACE = "org.bluez.GattService1"
GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"

SCRATCH_SVC_UUID = "a495ff20-c5b1-4b44-b512-1370f02d74de"

SCRATCHES = {"scratch1": {"uuid": "a495ff21-c5b1-4b44-b512-1370f02d74de",
                          "obj": None,
                          "value": 0},
             "scratch2": {"uuid": "a495ff22-c5b1-4b44-b512-1370f02d74de",
                          "obj": None,
                          "value": 0},
             "scratch3": {"uuid": "a495ff23-c5b1-4b44-b512-1370f02d74de",
                          "obj": None,
                          "value": 0},
             "scratch4": {"uuid": "a495ff24-c5b1-4b44-b512-1370f02d74de",
                          "obj": None,
                          "value": 0},
             "scratch5": {"uuid": "a495ff25-c5b1-4b44-b512-1370f02d74de",
                          "obj": None,
                          "value": 0}}


def generic_error_cb(error):
    print("D-Bus call failed: %s" % str(error))
    mainloop.quit()


def scratch_start_notify_cb():
    pass


def generate_cb(scratch_name):
    def scratch_notify_cb(iface, changed_props, _invalidated_props):
        if iface != GATT_CHRC_IFACE:
            return

        if not len(changed_props):
            return

        value = changed_props.get('Value', None)
        if not value:
            return

        SCRATCHES[scratch_name]["value"] = int(value[0])

        print("%s, %s %s" % (scratch_name, value, SCRATCHES[scratch_name]["value"]))

    return scratch_notify_cb


def start_client():
    for scratch in SCRATCHES.keys():
        iface = dbus.Interface(SCRATCHES[scratch]["obj"][0], DBUS_PROP_IFACE)
        iface.connect_to_signal("PropertiesChanged", generate_cb(scratch))

        SCRATCHES[scratch]["obj"][0].StartNotify(reply_handler=scratch_start_notify_cb,
                                                 error_handler=generic_error_cb,
                                                 dbus_interface=GATT_CHRC_IFACE)


def process_chrc(chrc_path):
    chrc = bus.get_object(BLUEZ_SERVICE_NAME, chrc_path)
    chrc_props = chrc.GetAll(GATT_CHRC_IFACE, dbus_interface=DBUS_PROP_IFACE)

    uuid = chrc_props['UUID']

    for scratch_name, scratch_data in SCRATCHES.iteritems():
        if uuid == scratch_data["uuid"]:
            SCRATCHES[scratch_name]["obj"] = (chrc, chrc_props)
            break

    return True


def process_bean_service(service_path):
    service = bus.get_object(BLUEZ_SERVICE_NAME, service_path)

    service_props = service.GetAll(GATT_SERVICE_IFACE,
                                   dbus_interface=DBUS_PROP_IFACE)
    uuid = service_props['UUID']

    if uuid != SCRATCH_SVC_UUID:
        print('Service is not a scratch service: ' + uuid)
        return False

    # Process the characteristics.
    chrc_paths = service_props['Characteristics']
    for chrc_path in chrc_paths:
        process_chrc(chrc_path)

    return True


def main():
    if len(sys.argv) < 2:
        print("One argument (mac) required")
        exit(1)

    mac = sys.argv[1]

    mac = mac.replace(":", "_")
    service_path = dbus.ObjectPath("/org/bluez/hci0/dev_%s/service0031/char0036" % mac)
    service_path = dbus.ObjectPath("/org/bluez/hci0/dev_%s/service0031" % mac)

    global mainloop
    mainloop = gobject.MainLoop()

    try:
        if not process_bean_service(service_path):
            print("Failed to process bean service")
            sys.exit(1)
    except dbus.DBusException as err:
        print(err.message)
        sys.exit(1)

    start_client()

    mainloop.run()


if __name__ == '__main__':
    main()