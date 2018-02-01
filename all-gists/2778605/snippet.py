import sys
import time
import usb

class Button:
   def __init__(self, vendor_id, device_id):
      """
      Find and open a USB HID device.
      """
      
      self.vendor_id = vendor_id
      self.device_id = device_id
      self.endpoint = 0x81

      self.device = self.getDevice(vendor_id, device_id)
      
      if self.device == None:
         raise DeviceNotFound, "No recognised device connected."

      self.handle = self.openDevice(self.device)
   
   def __del__(self):
      """
      Releases the device.
      """
      try:
         self.handle.releaseInterface()
         del self.handle
      except:
         pass
   
   def getDevice(self, vendor_id, device_id):
      """
      Searches the USB buses for a device matching the given vendor and device IDs.

      Returns a usb.Device, or None if the device cannot be found.
      """      

      busses = usb.busses()
   
      for bus in busses:
         devices = bus.devices
         for device in devices:
            if device.idVendor == vendor_id and device.idProduct == device_id:
               return device
   
      return None
   
   def openDevice(self, device):
      """
      Opens and claims the specified device. Returns a usb.DeviceHandle

      Also attempts to detach the kernel's driver from the device, if necessary.
      """

      handle = device.open()

      # Attempt to remove other drivers using this device. This is necessary
      # for HID devices.
      try:
         handle.detachKernelDriver(0)
      except:
         pass # Ignore failures here, the device might already be detached.

      handle.claimInterface(0)
      
      return handle

   def on_keydown(self):
      print "keydown event"

   def on_keyup(self):
      print "keyup event"

   def start(self):
      data = None
      while True:
         try:
            data = self.handle.interruptRead(self.endpoint, 8, 0)
         except:
            raise

         if data == (0, 0, 88, 0, 0, 0, 0, 0): # numeric keypad enter pressed
            self.on_keydown()
         elif data == (0, 0, 0, 0, 0, 0, 0, 0):
            self.on_keyup()
         
         data = None

class DeviceNotFound(Exception):
 def __init__(self,value):
    self.value = value
 def __str__(self):
    return repr(self.value)

if __name__ == "__main__":
   button = Button(0x1710, 0x5612)
   button.start()
