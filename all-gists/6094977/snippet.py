import smbus
import getopt
import sys
from time import *
from time import gmtime, strftime

# TODO: Factor out all device_write calls to some PCF8574 specific module ... 
#       will be different with another io expander

# communication from expander to display: high nibble first, then low nibble
# communication via i2c to the PCF 8547: bits are processed from highest to lowest (send P7 bit first) 


# General i2c device class so that other devices can be added easily
class i2c_device:
    def __init__(self, addr, port):
        self.addr = addr
        self.bus = smbus.SMBus(port)

    def write(self, byte):
        self.bus.write_byte(self.addr, byte)

    def read(self):
        return self.bus.read_byte(self.addr)

    def read_nbytes_data(self, data, n): # For sequential reads > 1 byte
        return self.bus.read_i2c_block_data(self.addr, data, n)


class ioexpander:
    def __init__(self):
        pass

class lcd:
    #initializes objects and lcd

    # LCD Commands
    LCD_CLEARDISPLAY        = 0x01
    LCD_RETURNHOME          = 0x02
    LCD_ENTRYMODESET        = 0x04
    LCD_DISPLAYCONTROL      = 0x08
    LCD_CURSORSHIFT         = 0x10
    LCD_FUNCTIONSET         = 0x20
    LCD_SETCGRAMADDR        = 0x40
    LCD_SETDDRAMADDR        = 0x80

    # Flags for display on/off control
    LCD_DISPLAYON           = 0x04
    LCD_DISPLAYOFF          = 0x00
    LCD_CURSORON            = 0x02
    LCD_CURSOROFF           = 0x00
    LCD_BLINKON             = 0x01
    LCD_BLINKOFF            = 0x00

    # Flags for display entry mode
    LCD_ENTRYRIGHT          = 0x00
    LCD_ENTRYLEFT           = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # Flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE  = 0x00
    LCD_MOVERIGHT   = 0x04
    LCD_MOVELEFT    = 0x00
    
    # flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00

    # flags for backlight control
    LCD_BACKLIGHT = 0x08
    LCD_NOBACKLIGHT = 0x00

    EN = 0b00000100  # Enable bit
    RW = 0b00000010  # Read/Write bit
    RS = 0b00000001  # Register select bit

    
    
    '''
    new pinout:
    ----------
0x80    P7 -  - D7     
0x40    P6 -  - D6
0x20    P5 -  - D5
0x10    P4 -  - D4    
    -----------
0x08    P3 -  - BL   Backlight ???
0x04    P2 -  - EN   Starts Data read/write 
0x02    P1 -  - RW   low: write, high: read   
0x01    P0 -  - RS   Register Select: 0: Instruction Register (IR) (AC when read), 1: data register (DR)
    '''
    
    def __init__(self, addr, port, withBacklight=True, withOneTimeInit=False):
        '''
        device writes!
        crosscheck also http://www.monkeyboard.org/tutorials/81-display/70-usb-serial-to-hd44780-lcd
        here a sequence is listed
        '''
        self.displayshift   = (self.LCD_CURSORMOVE |
                               self.LCD_MOVERIGHT)
        self.displaymode    = (self.LCD_ENTRYLEFT |
                               self.LCD_ENTRYSHIFTDECREMENT)
        self.displaycontrol = (self.LCD_DISPLAYON |
                               self.LCD_CURSOROFF |
                               self.LCD_BLINKOFF)
        

        if withBacklight:
            self.blFlag=self.LCD_BACKLIGHT
        else:
            self.blFlag=self.LCD_NOBACKLIGHT
        
        
        self.lcd_device = i2c_device(addr, port)
        
        # we can initialize the display only once after it had been powered on
        if(withOneTimeInit):
            self.lcd_device.write(0x20) 
            self.lcd_strobe()
            sleep(0.0100) # TODO: Not clear if we have to wait that long
            self.lcd_write(self.LCD_FUNCTIONSET | self.LCD_4BITMODE  | self.LCD_2LINE | self.LCD_5x8DOTS) # 0x28

        self.lcd_write(self.LCD_DISPLAYCONTROL | self.displaycontrol)   # 0x08 + 0x4 = 0x0C
        self.lcd_write(self.LCD_ENTRYMODESET   | self.displaymode)      # 0x06
        self.lcd_write(self.LCD_CLEARDISPLAY)                           # 0x01
        self.lcd_write(self.LCD_CURSORSHIFT    | self.displayshift)     # 0x14 
        self.lcd_write(self.LCD_RETURNHOME)
            
            
    # clocks EN to latch command
    def lcd_strobe(self):
        self.lcd_device.write((self.lcd_device.read() | self.EN | self.blFlag)) # | 0b0000 0100 # set "EN" high
        self.lcd_device.write(( (self.lcd_device.read() | self.blFlag) & 0xFB)) # & 0b1111 1011 # set "EN" low

    # write data to lcd in 4 bit mode, 2 nibbles
    # high nibble is sent first
    def lcd_write(self, cmd):
        
        #write high nibble first
        self.lcd_device.write( (cmd & 0xF0) | self.blFlag )
        hi= self.lcd_device.read()
        self.lcd_strobe()
        
        # write low nibble second ...
        self.lcd_device.write( (cmd << 4) | self.blFlag )
        lo= self.lcd_device.read()
        self.lcd_strobe()
        self.lcd_device.write(self.blFlag)
    
    
    # write a character to lcd (or character rom) 0x09: backlight | RS=DR
    # works as expected
    def lcd_write_char(self, charvalue):
        controlFlag = self.blFlag | self.RS
        
        # write high nibble
        self.lcd_device.write((controlFlag | (charvalue & 0xF0)))
        self.lcd_strobe()
        
        # write low nibble
        self.lcd_device.write((controlFlag | (charvalue << 4)))
        self.lcd_strobe()
        self.lcd_device.write(self.blFlag)


    # put char function
    def lcd_putc(self, char):
        self.lcd_write_char(ord(char))

    def _setDDRAMAdress(self, line, col):
        # we write to the Data Display RAM (DDRAM)        
        # TODO: Factor line offsets for other display organizations; this is for 20x4 only 
        if line == 1:
            self.lcd_write(self.LCD_SETDDRAMADDR | (0x00 + col) )
        if line == 2:
            self.lcd_write(self.LCD_SETDDRAMADDR | (0x40 + col) )
        if line == 3:
            self.lcd_write(self.LCD_SETDDRAMADDR | (0x14 + col) )
        if line == 4:
            self.lcd_write(self.LCD_SETDDRAMADDR | (0x54 + col) )
        

    # put string function
    def lcd_puts(self, string, line):
        self._setDDRAMAdress(line, 0)
        for char in string:
            self.lcd_putc(char)

    # clear lcd and set to home
    def lcd_clear(self):
        # self.lcd_write(0x10)
        self.lcd_write(self.LCD_CLEARDISPLAY)
        # self.lcd_write(0x20)
        self.lcd_write(self.LCD_RETURNHOME)

    # add custom characters (0 - 7)
    def lcd_load_custon_chars(self, fontdata):
        self.lcd_device.bus.write(0x40);
        for char in fontdata:
            for line in char:
                self.lcd_write_char(line)

# Let them know how it works
def usage():
    print 'Usage: lcdui.py --init --debug --backlightoff'

# Handle the command line arguments
def main():    
    initFlag=False
    debug=False
    backlight=True
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],"idb",["init","debug","backlightoff"])

    except getopt.GetoptError:
        usage()
        sys.exit(2)


    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-i", "--init"):
            initFlag = True
        elif opt in ("-d", "--debug"):
            debug = True
        elif opt in ("-b", "--backlightoff"):
            backlight = False
    
    if initFlag:
        print "Doing initial init ..."
    else:
        print "Skipping init ..."
    
    device = lcd(0x27,1,backlight, initFlag)  
    device.lcd_puts("01234567890123456789",1)
    device.lcd_puts("012345 Zeile 2 56789",2)
    device.lcd_puts("012345 Zeile 3 56789",3)
    device.lcd_puts(strftime("%Y-%m-%d %H:%M:%S", gmtime()),4)
    sleep(3)
    device.lcd_clear()
    device.lcd_puts("    Simple Clock    ",1)
    while True:
        device.lcd_puts(strftime("%Y-%m-%d %H:%M:%S ", gmtime()),3)
        sleep(1)

if __name__ == '__main__':
    main()
