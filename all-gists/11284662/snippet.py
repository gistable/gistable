import select
import socket
import sys

import objc
from PyObjCTools import AppHelper

objc.loadBundle("CoreBluetooth", globals(),
    bundle_path=objc.pathForFramework(u'/System/Library/Frameworks/IOBluetooth.framework/Versions/A/Frameworks/CoreBluetooth.framework'))

blebee_service = CBUUID.UUIDWithString_(u'EF080D8C-C3BE-41FF-BD3F-05A5F4795D7F')
blebee_rx = CBUUID.UUIDWithString_(u'A1E8F5B1-696B-4E4C-87C6-69DFE0B0093B')
blebee_tx = CBUUID.UUIDWithString_(u'1494440E-9A58-4CC0-81E4-DDEA7F74F623')

class RobotDelegate(object):
    def __init__(self):
        self.manager = None
        self.peripheral = None

        self.service = None

        self.rx = None
        self.tx = None

        self.comms = None

    def centralManagerDidUpdateState_(self, manager):
        print repr(manager), "done it!"
        self.manager = manager
        manager.scanForPeripheralsWithServices_options_([blebee_service], None)

    def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(self, manager, peripheral, data, rssi):
        self.peripheral = peripheral
        manager.connectPeripheral_options_(peripheral, None)

    def centralManager_didConnectPeripheral_(self, manager, peripheral):
        print repr(peripheral)
        self.peripheral.setDelegate_(self)
        self.peripheral.discoverServices_([blebee_service])

    def centralManager_didFailToConnectPeripheral_error_(self, manager, peripheral, error):
        print repr(error)

    def centralManager_didDisconnectPeripheral_error_(self, manager, peripheral, error):
        print repr(error)
        AppHelper.stopEventLoop()

    def peripheral_didDiscoverServices_(self, peripheral, services):
        self.service = self.peripheral.services()[0]
        self.peripheral.discoverCharacteristics_forService_([blebee_rx, blebee_tx], self.service)

    def peripheral_didDiscoverCharacteristicsForService_error_(self, peripheral, service, error):
        print repr(service)
        print repr(error)

        for characteristic in self.service.characteristics():
            if characteristic.UUID() == blebee_rx:
                self.rx = characteristic
                self.peripheral.setNotifyValue_forCharacteristic_(True, self.rx)
            elif characteristic.UUID() == blebee_tx:
                self.tx = characteristic

        print repr(self.rx.UUID())
        print repr(self.tx.UUID())

    def peripheral_didWriteValueForCharacteristic_error_(self, peripheral, characteristic, error):
        print repr(error)

    def peripheral_didUpdateNotificationStateForCharacteristic_error_(self, peripheral, characteristic, error):
        print "Receiving notifications"

    def peripheral_didUpdateValueForCharacteristic_error_(self, peripheral, characteristic, error):
        self.comms.send(characteristic.value().bytes().tobytes())
        print repr(characteristic.value().bytes().tobytes())

    def shutdown(self):
        if self.peripheral is not None:
            self.manager.cancelPeripheralConnection_(self.peripheral)
        else:
            AppHelper.stopEventLoop()

    def send(self, byte):
        byte = NSData.dataWithBytes_length_(byte, 1)
        self.peripheral.writeValue_forCharacteristic_type_(byte, self.tx, 0)

class CommsManager(object):
    def __init__(self, robot):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind(("127.0.0.1", 9999))
        self.listener.listen(1)

        self.connection = None

        self.robot = robot
        self.robot.comms = self

    def loop(self):
        endpoints = [sys.stdin, self.listener]
        if self.connection is not None:
            endpoints.append(self.connection)

        r, w, e = select.select(endpoints, [], [], 0)
        if sys.stdin in r:
            delegate.shutdown()
            return
        if self.listener in r:
            self.connection, _ = self.listener.accept()
        if self.connection in r:
            c = self.connection.recv(1)
            if len(c) == 0:
                print "closed"
                self.connection.close()
                self.connection = None
            elif c not in ('\r', '\n'):
                print repr(c)
                self.robot.send(c)

        AppHelper.callLater(0.1, self.loop)

    def send(self, data):
        while len(data):
            sent = self.connection.send(data)
            data = data[sent:]

delegate = RobotDelegate()
manager = CBCentralManager.alloc()
manager.initWithDelegate_queue_options_(delegate, None, None)

comms = CommsManager(delegate)

print repr(manager)

AppHelper.callLater(0.1, comms.loop)
AppHelper.runConsoleEventLoop()
