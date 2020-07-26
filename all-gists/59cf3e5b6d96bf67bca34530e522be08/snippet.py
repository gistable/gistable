# Very simple python program view BMP images sent via Serial from Arduino or other microcontoller boards
# The program sents the charachter '0' to Serial, to trigger the Arduino board to send the image.
# Only tested with 320x240 pixel images.
# Change root.geometry('320x280') to some other size if your image is bigger

# Requires Python 2.7 - probably won't work in Python 3 without changes
# Requires Pillow (PIL) image library. Install using pip install Pillow from your command line.

from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog

#pip install Pillow
from PIL import Image, ImageTk
import serial
from time import sleep
import sys
import StringIO
import os


class Application(Frame):

    def destroy(self):
        #print "destroy"        
        try:
            if (self.ser.isOpen() == True):
                #print "closing serial port"
                self.ser.close()
            else:
                pass
                #print "Serial port not open"
        except:
            pass
            #print "Serial variable not defined"
                
    def take_photo(self):
        self.initSerial()

    def setComPort(self,chosenComPort):
        #print "Set com port to "+chosenComPort
        self.commPort = chosenComPort

    def serial_ports(self):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def saveImage(self):
        print "Save image"
        try:
            if (self.photoLabel.imgBytes == ""):
                self.photoLabel = Label(text="No image to save.")
                self.photoLabel.pack()
                return
        except:
            self.photoLabel = Label(text="No image to save.")
            self.photoLabel.pack()
            return
            
        fileName = tkFileDialog.asksaveasfilename(initialdir = "/",
                                                  title = "Select file",
                                                  filetypes = (("BMP","*.bmp"),),
                                                  defaultextension='.bmp' )
        imageFile = open(fileName, "wb")
        imageFile.write(self.photoLabel.imgBytes)
        imageFile.close()
       
        
    def createWidgets(self):

        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"]   = "red"
        self.QUIT["command"] =  self.quit

        self.QUIT.pack({"side": "left"})

        self.takePhotoButton = Button(self)
        self.takePhotoButton["text"] = "Take Photo"
        self.takePhotoButton["command"] = self.take_photo
        self.takePhotoButton.pack({"side": "left"})

# Add com ports to menu        
        menubar = Menu(root)
        fileMenu = Menu(menubar, tearoff=0)
        fileMenu.add_command(label="Save", command=self.saveImage)
        menubar.add_cascade(label="File", menu=fileMenu)
         
        comPortMenu = Menu(menubar, tearoff=0)
        for member in self.serial_ports():
            comPortMenu.add_command(label=member, command=lambda m=member: self.setComPort(m))
        menubar.add_cascade(label="Select COM port", menu=comPortMenu)

        root.config(menu=menubar)

    def byte2Int(self,b):
        return int(b.encode('hex'), 16)
        
    def readImage(self,ser):
            #TOTAL_IMAGE_SIZE_IN_BYTES = 320 * 240 * 3 + 54
            while ser.in_waiting !=0 :
                ser.read(ser.in_waiting)
                sleep(0.1)

			# CHANGE THIS LINE IF YOU WANT TO SEND SOMETHING ELSE TO TRIGGER SENDING THE IMAGE FROM THE ARDUINO
            ser.write('0')

            imgBytes = bytes()
            # image header starts with BM then the next 4 bytes are the length as 32 bits.
            while len(imgBytes) < 6:
                imgBytes += ser.read(ser.in_waiting)

            # calculate the total size that will arrive via serial.
            TOTAL_IMAGE_SIZE_IN_BYTES =  self.byte2Int(imgBytes[2])+self.byte2Int(imgBytes[3])*256 + self.byte2Int(imgBytes[4])*256*256 + self.byte2Int(imgBytes[5])*256*256*256

            #loop until all bytes are received....
            #To Do. Timeout !!    
            while len(imgBytes) < TOTAL_IMAGE_SIZE_IN_BYTES:
                imgBytes += ser.read(ser.in_waiting)


            photo = ImageTk.PhotoImage(data=imgBytes)
            root.geometry(str(photo.width())+"x"+str(photo.height()+50))
            try:
                self.photoLabel
                self.photoLabel.config(image=photo)
                self.photoLabel.imgBytes = imgBytes
            except:
                self.photoLabel = Label(image=photo)
                self.photoLabel.imgBytes = imgBytes

                


			
            self.photoLabel.image = photo # keep a reference!
            self.photoLabel.pack()
                        
    
    def initSerial(self):
        try:
            self.commPort
            try:
            # configure the serial connections (the parameters differs on the device you are connecting to)
                self.ser = serial.Serial(
                        port=self.commPort,
                        baudrate=115200,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS)

                if ( self.ser.isOpen() == False):
                    self.ser.open()
                    #print 'Serial opened'
                    self.readImage(ser)
                    self.ser.close()
                    #print 'Serial closed'
                else:
                    #print 'Serial already open '
                    self.readImage(self.ser)
                    self.ser.close()
                    #print 'Serial closed'
            except:
                print "Serial port error"
        except:
            #print "Please select a com port"
            self.photoLabel = Label(text="Please select a com port first")
            self.photoLabel.pack()

    def __init__(self, main=None):
        Frame.__init__(self, main)
        self.pack()
        self.createWidgets()

root = Tk()
root.wm_title("STM32 OV7670")
root.geometry('320x50')


app = Application(main=root)
app.mainloop()
try:
    root.destroy()
except:
    pass
