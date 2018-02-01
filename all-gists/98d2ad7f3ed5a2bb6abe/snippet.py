#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__  = ('Kaan Akşit')
                                                                                                                                     
try:                                                                                                                                 
    import sys,time                                                                                                                  
    from array import array                                                                                                          
    from jnius import autoclass                                                                                                      
    from jnius import cast                                                                                                           
except ImportError, err:                                                                                                             
    print "couldn't load module. %s" % (err)                                                                                         
    sys.exit()                                                                                                                       
                                                                                                                                     
# Class for serial communication using USB-OTG cable in an Android OS.                                                               
class Serial:                                                                                                                        
    def __init__(self,port,speed):                                                                                                   
        self.Context             = autoclass('android.content.Context')                                                              
        self.UsbConstants        = autoclass('android.hardware.usb.UsbConstants')                                                    
        self.UsbDevice           = autoclass('android.hardware.usb.UsbDevice')                                                       
        self.UsbDeviceConnection = autoclass('android.hardware.usb.UsbDeviceConnection')                                             
        self.UsbEndpoint         = autoclass('android.hardware.usb.UsbEndpoint')                                                     
        self.UsbInterface        = autoclass('android.hardware.usb.UsbInterface')                                                    
        self.UsbManager          = autoclass('android.hardware.usb.UsbManager')                                                      
        self.UsbRequest          = autoclass('android.hardware.usb.UsbRequest')                                                      
        self.PythonActivity      = autoclass('org.renpy.android.PythonActivity')                                                     
        self.activity            = self.PythonActivity.mActivity                                                                     
        self.speed               = speed                                                                                             
        self.port                = port                                                                                              
        self.ReadCache           = []                                                                                                
        self.usb_mgr             = cast(self.UsbManager, self.activity.getSystemService(self.Context.USB_SERVICE))                   
        print [d.getKey() for d in self.usb_mgr.getDeviceList().entrySet().toArray()]
        self.device              = self.usb_mgr.getDeviceList().get(port)
        self.cmd                 = 'k00'
        if self.device:
            Intent                = autoclass('android.content.Intent')
            PendingIntent         = autoclass('android.app.PendingIntent')
            ACTION_USB_PERMISSION = "com.access.device.USB_PERMISSION"
            intent                = Intent(ACTION_USB_PERMISSION)
            pintent               = PendingIntent.getBroadcast(self.activity,0,intent,0)
            self.usb_mgr.requestPermission(self.device,pintent)
            if self.usb_mgr.hasPermission(self.device):
                print 'Device permission granted!'
                print 'InterfaceCount: ', self.device.getInterfaceCount()
                self.intf          = cast(self.UsbInterface, self.device.getInterface(0))
                self.UsbConnection = cast(self.UsbDeviceConnection,self.usb_mgr.openDevice(self.device))
                print self.UsbConnection
                self.UsbConnection.claimInterface(self.intf, True)
                print 'SerialNumber: ', self.UsbConnection.getSerial()
                self.UsbConnection.controlTransfer(0x40, 0, 0, 0, None, 0, 0)
                self.UsbConnection.controlTransfer(0x40, 0, 1, 0, None, 0, 0)
                self.UsbConnection.controlTransfer(0x40, 0, 2, 0, None, 0, 0)
                self.UsbConnection.controlTransfer(0x40, 2, 0, 0, None, 0, 0)               
                self.UsbConnection.controlTransfer(0x40, 3, 0x0034, 0, None, 0, 0)               
                self.UsbConnection.controlTransfer(0x40, 4, 8, 0, None, 0, 0)               
                for i in xrange(0, self.intf.getEndpointCount()):
                    if self.intf.getEndpoint(i).getType() == self.UsbConstants.USB_ENDPOINT_XFER_BULK:
                        if self.intf.getEndpoint(i).getDirection() == self.UsbConstants.USB_DIR_IN:
                            self.epIN  = self.intf.getEndpoint(i)
                        elif self.intf.getEndpoint(i).getDirection() == self.UsbConstants.USB_DIR_OUT:
                            self.epOUT = self.intf.getEndpoint(i)
            else:
                print 'Device permission not granted!'
        else:
            print 'Device not found.'
            sys.exit()
        return
    def send(self,msg):   
        MsgOut    = msg
        MsgOutHex = map(ord,MsgOut)
        self.UsbConnection.bulkTransfer(self.epOUT, MsgOutHex, len(MsgOutHex), 0)
        return True
    def read(self,BufSize=35):
        time.sleep(0.03)
        response = [0]*BufSize
        length   = self.UsbConnection.bulkTransfer(self.epIN, response, len(response), 50)
        if length >= 0:
            self.ReadCache = response
        return True
    def asyncRead(self):
        self.send(self.cmd)
        self.read()
        return
    def disconnet(self):
        self.UsbConnection.close()
        return True

def main():
    pass
    return True

# Call for main definition upon initialization.
if __name__ == '__main__':
     sys.exit(main())
