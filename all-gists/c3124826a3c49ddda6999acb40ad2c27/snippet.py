#!/usr/bin/env python
# coding: utf-8

from PIL import Image, ImageOps
import numpy
import serial


class SM1_21:
    def __init__(self, port='/dev/ttys0', baud=115200):
        self.printer = serial.Serial(port, baud)
        # self.printer.write('\x1b\x5f')  # フラッシュメモリのパラメータ初期化
        self.printer.write('\x1c\x26')
        self.printer.write('\x1c\x43\x01')

    def command(self, text):
        self.printer.write(text)

    def text(self, text, flag=0, bold=0):
        if bold == 1:
            self.printer.write('\x1b\x47\x01')
        else:
            self.printer.write('\x1b\x45\x00')

        self.printer.write(text.encode('shift-jis', 'replace'))

        if flag == 1:
            self.printer.write('\x0a')

    def output(self):
        self.printer.write('\x0a')

    def tab(self):
        self.printer.write('\x09' + 'h')

    def image(self, img_path, threshold=200, pitch=200):
        im = Image.open(img_path)

        width = im.size[0]
        height = im.size[1]

        mag = 384.0 / width
        color = 0
        inv = 0

        Aheight = int(mag * float(height))
        print Aheight

        im2 = im.resize((384, Aheight), Image.ANTIALIAS)
        im2 = ImageOps.grayscale(im2)
        if inv == 1:
            im2 = ImageOps.invert(im2)
        im2.save('test2.jpg', 'JPEG')

        imgArray = numpy.asarray(im2)
        imgArray.flags.writeable = True

        for j in range(Aheight - 1):
            for i in range(383):
                f = imgArray[j][i]
                if f > threshold:
                    imgArray[j][i] = 255
                else:
                    imgArray[j][i] = 0

        pilImg = Image.fromarray(numpy.uint8(imgArray))
        pilImg.save('test3.jpg')

        c = 0
        count = 0
        count2 = 0

        for j in range(Aheight):
            if count == 0:
                if (Aheight - 1) - j < pitch:
                    self.printer.write('\x1d\x2a\x30')
                    self.printer.write(chr(Aheight - j))
                else:
                    self.printer.write('\x1d\x2a\x30')
                    self.printer.write(chr(pitch))
            for i in range(48):
                for n in range(8):
                    if imgArray[j][(i * 8) + n] > 100:
                        a = color
                    else:
                        a = not (color)
                    c = (c << 1) | a
                self.printer.write(chr(c))
                c = 0
            count += 1
            if count >= pitch:
                count2 += 1
                self.printer.write('\x1d\x2f\x00')
                count = 0
        self.printer.write('\x1d\x2f\x00')
        self.printer.write('\n' * 3)

if __name__ == '__main__':
    p = SM1_21(port='/dev/tty.SM1-21-SerialPortDevB')
    p.image('1327.jpg')
    raw_input()
