#!/usr/bin/python
from Foundation import NSBundle

IOBluetooth       = NSBundle.bundleWithIdentifier_('com.apple.Bluetooth')
IOBluetoothDevice = IOBluetooth.classNamed_('IOBluetoothDevice')

# remove configured devices
try:
    devices = list(IOBluetoothDevice.configuredDevices())
except:
    devices = []
for device in devices:
    try:
        device.remove()
    except:
        pass

# remove paired devices
try:
    devices = list(IOBluetoothDevice.pairedDevices())
except:
    devices = []
for device in devices:
    try:
        device.remove()
    except:
        pass

# remove favorite devices
try:
    devices = list(IOBluetoothDevice.favoriteDevices())
except:
    devices = []
for device in devices:
    try:
        device.remove()
    except:
        pass
