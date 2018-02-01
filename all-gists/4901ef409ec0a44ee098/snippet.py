import gc
import machine
import pyb
import time
import network

# Configure GPIO pins 0 and 2 to be used for
# the I²C interface
iic = machine.I2C(pyb.Pin(2), pyb.Pin(0))

# From the docs here: https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf
COMMAND = b'\x80'
DATA = b'\x40'

DISPLAY_ON = COMMAND+b'\xaf'
DISPLAY_OFF = COMMAND+b'\xae'
CHARGE_PUMP_SET = COMMAND+b'\x8d'
CHARGE_PUMP_ON = COMMAND+b'\x14'
TOP_TO_BOTTOM = COMMAND+b'\xC8'
LEFT_TO_RIGHT = COMMAND+b'\xA1'

# Each I²C device has an address, 60 (0x3c) is the address of the display
DISPLAY = 60
# One row (page in the docs) is 8 pixels high
FILL_ROW = lambda row,val: iic.writeto(DISPLAY, COMMAND+(0xb0+row).to_bytes(1)+DATA+(val.to_bytes(1)) * 128)
# Move the 'graphics cursor' to position col, row.  Col is offset from left in pixels, row is offset from top in pixels*8
GOTO = lambda col,row: iic.writeto(DISPLAY, COMMAND+(0xb0+row).to_bytes(1)+COMMAND+(col&0x0f).to_bytes(1)+COMMAND+(0x10|col>>4).to_bytes(1))

# Make the display be blank
def CLEAR():
    for i in range(8):
        FILL_ROW(i, 0x00)


# Make sure the display is off while we set things up
iic.writeto(DISPLAY, DISPLAY_OFF)
# Because the display is powered from the board, you have to tell it to
# boost the voltages internally before anything happens
iic.writeto(DISPLAY, CHARGE_PUMP_SET)
iic.writeto(DISPLAY, CHARGE_PUMP_ON)

# Row 0 defaults to the bottom of the screen, This makes Row 0 the top
iic.writeto(DISPLAY, TOP_TO_BOTTOM)
# Column 0 defaults to the right edge of the screen, This makes it the left
iic.writeto(DISPLAY, LEFT_TO_RIGHT)
# Start with a blank screen (display data can be random on power-on)
CLEAR()

# Turn the display on
iic.writeto(DISPLAY, DISPLAY_ON)
# Move the grahics cursor top top-left
GOTO(0,0)
# Show some lines on the screen so we know something is going on
FILL_ROW(2, 0xaa)

# Configure the wifi networking
network.wifi_mode(1)
network.phy_mode(1)
wlan=network.WLAN()
wlan.connect('<WIFI SSID>', '<WIFI PASS>')
ip = '0.0.0.0'
while ip == '0.0.0.0':
    ip, _, gw, _ = wlan.ifconfig()
    time.sleep(0.1)

# Connect to the telnet server
import socket
_, _, _, _, addr = socket.getaddrinfo("towel.blinkenlights.nl", 23)[0]
sock = socket.socket()
sock.connect(addr)

# Set blocking = false to alllow us to just get the data that's arrived
# without worrying too much about how much is there
sock.setblocking(False)

# The star wars ascii data is output to an 80 x 18 CHARACTER terminal window.
# Out display is 128x64 PIXELS, so we have to do some scaling.
# I decided each character should take up 2x4 pixels, meaning the size of our 'window'
# would be 160 x 72 pixels big.  If we ignore the pixels that fall outside this area
# (Most of the action happens in middle of the screen anyway) then we can fill the display
# with pretty action without doing too much maths (which might be a bit slow)

# This lookup table allows us to map the ascii-art of the movie
# to a 2x4 pixel block on screen.
# Basically, if the server sends a '<' char, then:
# This maps tothe values 0x6 and 0x9
# Which are 2+4 (6) and 8+1 (9)
# So the pixels become:
#  1  □  █
#  2  █  □
#  4  █  □
#  8  □  █
CHARS={
    ord('.'): (0x4, 0x4),
    ord('-'): (0x2, 0x2),
    ord('_'): (0x8, 0x8),
    ord('|'): (0xf, 0x0),
    ord('/'): (0xc, 0x3),
    ord('\\'): (0x3, 0xc),
    ord('='): (0x6, 0x6),
    ord('c'): (0xf, 0x9),
    ord('<'): (0x6, 0x9),
    ord('>'): (0x9, 0x6),
}

# Micropython bytes handing is a teensy bit weird (this might just be python3)
# If you index into a bytes array, you get an integer value.
# The data being read off the socket comes in bytes (good), but to do compariasons
# we need to know the numeric ordinal of several characters.  Doing this outside the loop
# is probably better than inside
SPACE = ord(' ')
CR = ord('\r')

# Keep track of our current position on screen
row = 0
col = 0

# The display writes 8 vertical pixels at a time, and for speed reasons, we
# want to write one row of 8 pixels in a go.  Each line
# from the telnet connection will be 4 pixels high, so we need to buffer up 2 lines
# worth of ascii art at a time, so they can be sent to the display in one go.
# rowbits, being an array of 128 x 8bits, is perfect for this, as it also matches
# the format the display expects for updating a row.
rowbits = bytearray(128)

# In a perfect world, each 'thing' we would have to handle coming from the server
# would be exactly 1 byte long.  Unfortunately newlines are sent as two bytes (CR + LF),
# and escape sequences more.  It seems like they're only using 2-byte escape sequences.
# Because of this, if a CR (13), or ESC (27) char is seen, we set this skip value, to
# ignore the next N bytes.  This approach is 'good enough' for a reasonable output
skip = 0

# Writes the current rowbits data to the screen, using the 'row' global to work out where on
# the screen it goes
def draw_row():
    global rowbits
    screenrow = int(row/2 - 2.4)
    if screenrow >= 0 and screenrow <= 8:
        GOTO(0, screenrow)
        iic.writeto(DISPLAY, DATA+rowbits)
    rowbits = bytearray(128)

# The full movie is > 1h long, so for our purposes, the loop never ends
while True:
    # Read up to 200 bytes from the network. It's easy to run out of memory by setting
    # the number of bytes too high
    data = sock.read(200)
    # For some reason, non-blocking reads that return no data
    # return None, rather than an empty byte string
    if data is None:
        # Give the CPU some time to find some data
        time.sleep(0.01)
        continue
    for byte in data:
        if skip:
            skip -= 1
            continue
        # 0x1b = escape byte, we assume this means to clear the screen
        if byte == 0x1b:
            skip = 2
            row += 1 # Increment the row, because we need to flush the current row before resetting
            draw_row()
            GOTO(0,0)
            row = 0
            gc.collect() # Not 100% sure gc is needed here, but I was having memory issues
        elif byte == CR: # CR indicates newline
            skip = 1
            row += 1
            col = 0
            # After finishing every other row, flush the data to display
            if row % 2 == 0:
                draw_row()
        elif byte == SPACE:
            col += 1
        else:
            screencol = (col-4)*2 # Map a character col to screen pixel
            if screencol >= 0 and screencol < 127: # Ignore pixels that are off-screen
                # Look up the right shape to draw using the character.  Default to a solid block
                left, right = CHARS.get(byte, (0x0f, 0x0f))
                if row % 2: # Row 1 appears in the top half of the row bytes, row 2 in the bottom half
                    left <<= 4
                    right <<= 4
                rowbits[screencol] |= left
                rowbits[screencol+1] |= right
            col += 1