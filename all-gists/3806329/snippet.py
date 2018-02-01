#!/usr/bin/env python

import sys, termios, StringIO
import Image # PIL

class SixelConverter:

    def __init__(self, image, f8bit = False):

        if f8bit: # 8bit mode
            self.DCS='\x90'
            self.ST='\x9c'
        else:
            self.DCS='\x1bP'
            self.ST='\x1b\\'

        self.palette = image.getpalette()
        self.data = image.getdata()
        self.width, self.height = image.size

    def __write_header(self, output):
        # start Device Control String (DCS)
        output.write(self.DCS)
    
        # write header
        output.write('0;0;8q"1;1')

    def __write_palette_section(self, output):

        palette = self.palette

        # write palette section
        for i in range(0, len(palette), 3):
            output.write('#' + str(i / 3) + ";2;")
            output.write(str(palette[i] * 100 / 256) + ";")
            output.write(str(palette[i + 1] * 100 / 256) + ";")
            output.write(str(palette[i + 2] * 100 / 256))

    def __write_body_section(self, output):

        data = self.data

        #write body section
        height = self.height
        width = self.width
        for y in range(0, height):
            cachedNo = data[y * width]
            count = 1
            for x in range(0, width):
                colorNo = data[y * width + x]
                if colorNo == cachedNo:
                    count += 1
                    continue
                c = chr(pow(2, y % 6) + 63)
                if count > 1:
                    output.write('#' + str(cachedNo) + '!' + str(count) + c)
                    count = 1
                else:
                    output.write('#' + str(cachedNo) + c)
                cachedNo = colorNo
            if count > 1:
                output.write('#' + str(cachedNo) + '!' + str(count) + c)
            else:
                output.write('#' + str(cachedNo) + c)
            output.write('$') # write line terminator
            if y % 6 == 5:
                output.write('-') # write sixel line separator
        
    def __write_terminator(self, output):
        # write ST
        output.write(self.ST) # terminate Device Control String

    def getvalue(self):

        output = StringIO.StringIO()

        try:
            self.__write_header(output)
            self.__write_palette_section(output)
            self.__write_body_section(output)
            self.__write_terminator(output)
            
            value = output.getvalue()

        finally: 
            output.close()

        return value
 
class CellSizeDetector:
    def __set_raw(self):
        fd = sys.stdin.fileno()
        backup = termios.tcgetattr(fd)
        try:
            new = termios.tcgetattr(fd)
            new[0] = 0 # c_iflag = 0
    #        new[3] = 0 # c_lflag = 0
            new[3] = new[3] &~ (termios.ECHO | termios.ICANON)
            termios.tcsetattr(fd, termios.TCSANOW, new)
        except:
            termios.tcsetattr(fd, termios.TCSANOW, backup)
        return backup
    
    def __reset_raw(self, old):
        fd = sys.stdin.fileno()
        termios.tcsetattr(fd, termios.TCSAFLUSH, old)
    
    def __get_report(self, query):
        sys.stdout.write(query)
        result = ''
        while True:
            c = sys.stdin.read(1)
            if c == 't':
                break
            result += c
        return result

    def get_size(self):

        backup_termios = self.__set_raw()
        try: 
            (height, width) = self.__get_report("\x1b[14t").split(';')[1:]
            (row, column) = self.__get_report("\x1b[18t").split(';')[1:]
            
            char_width = int(width) / int(column)
            char_height = int(height) / int(row)
        finally: 
            self.__reset_raw(backup_termios)
        return char_width, char_height


class SixelWriter:
    
    def __init__(self, f8bit = False):
        if f8bit: # 8bit mode
            self.CSI='\x9b'
        else:
            self.CSI='\x1b['

    def save_position(self):
        sys.stdout.write('\x1b7')

    def restore_position(self):
        sys.stdout.write('\x1b8')

    def move_x(self, n, fabsolute):
        sys.stdout.write(self.CSI)
        if fabsolute:
            sys.stdout.write(str(n) + '`')
        else:
            if n > 0:
                sys.stdout.write(str(n) + 'C')
            elif n < 0:
                sys.stdout.write(str(-n) + 'D')

    def move_y(self, n, fabsolute):
        sys.stdout.write(self.CSI)
        if fabsolute:
            sys.stdout.write(str(n) + 'd')
        else:
            if n > 0:
                sys.stdout.write(str(n) + 'B')
            elif n < 0:
                sys.stdout.write(str(-n) + 'A')

    def draw(self, filename, abs, x = None, y = None, w = None, h = None):
        image = Image.open(filename)
        image = image.convert("P")

        if not (w is None and h is None):
            width, height = image.size
            if w == None:
                h = height
            if h == None:
                w = width
            print h,'-', w
            image = image.resize((w, h))

        self.save_position()

        try:
            if not x is None:
                self.move_x(x, abs)

            if not y is None:
                self.move_y(y, abs)

            sixel_converter = SixelConverter(image, options.f8bit)
            sys.stdout.write(sixel_converter.getvalue())

        finally:
            self.restore_position()
        
if __name__ == '__main__':

    import optparse, re

    parser = optparse.OptionParser()
    
    parser.add_option("-8", "--8bit-mode",
              action="store_true",
              dest="f8bit",
              help="Generate a sixel image for 8bit terminal or printer")
    
    parser.add_option("-7", "--7bit-mode",
              action="store_false",
              dest="f8bit",
              help="Generate a sixel image for 7bit terminal or printer")
 
    parser.add_option("-r", "--relative-position",
                      default=False,
                      action="store_false",
                      dest="fabsolute",
                      help="Treat specified position as relative one")
  
    parser.add_option("-a", "--absolute-position",
                      action="store_true",
                      dest="fabsolute",
                      help="Treat specified position as absolute one")
     
    parser.add_option("-x", "--left",
                      dest="left",
                      help="Left position in cell size, or pixel size with unit 'px'")

    parser.add_option("-y", "--top",
                      dest="top",
                      help="Top position in cell size, or pixel size with unit 'px'")
     
    parser.add_option("-w", "--width",
                      dest="width",
                      help="Width in cell size, or pixel size with unit 'px'")
     
    parser.add_option("-e", "--height",
                      dest="height",
                      help="Height in cell size, or pixel size with unit 'px'")

    options, args = parser.parse_args()
    filename = args[0]

    char_width, char_height = CellSizeDetector().get_size()

    left = options.left
    if not left is None:
        pos = left.find("px")
        if pos == len(left) - 2:
            left = int(left[:pos]) / char_width 
        else:
            left = int(left) 

    top = options.top
    if not top is None:
        pos = top.find("px")
        if pos == len(top) - 2:
            top = int(top[:pos]) / char_width 
        else:
            top = int(top) 
 
    width = options.width
    if not width is None:
        pos = width.find("px")
        if pos == len(width) - 2:
            width = int(width[:pos]) 
        else:
            width = int(width) * char_width
 
    height = options.height
    if not height is None:
        pos = height.find("px")
        if pos == len(height) - 2:
            height = int(height[:pos]) 
        else:
            height = int(height) * char_height
               
    writer = SixelWriter(options.f8bit)
    writer.draw(filename, abs = options.fabsolute,
                x = left, y = top, w = width, h = height) 


