#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import time

import Image
import ImageDraw
import ImageFont

from Adafruit_LED_Backpack import Matrix8x8


def print_8x8(image):
    display.clear()
    display.set_image(image)
    display.write_display()


a = u'동해물과 백두산이 마르고 닳도록 하느님이 보우하사  '

display = Matrix8x8.Matrix8x8()
display.begin()
image = Image.new('1', (1250,8))
draw = ImageDraw.Draw(image)

font = ImageFont.truetype('AppleGothic.ttf', 8)
draw.text((0, 0), a, font=font, fill=255)
w, h = draw.textsize(a, font=font)

while True:
      for x in range(0,w-1):
          b = image.crop((x, 0, x+8, 8))
          print_8x8(b)
          time.sleep(0.02)
          