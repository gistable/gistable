#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import StringIO

import requests
import PIL.Image
import tesserwrap


#: https://github.com/gregjurman/tesserwrap
tesseract = tesserwrap.tesseract()


def distinguish_captcha(image_url, show_origin_image=True):
    #: preprocess
    image_bytes = requests.get(image_url).content
    origin_image = PIL.Image.open(StringIO.StringIO(image_bytes))
    image = origin_image.point(lambda p: p * 1.5)\
        .point(lambda p: 255 if p > 200 else 0)\
        .convert("1")
    #: distinguish the text
    text = tesseract.ocr_image(image)
    #: show the origin image
    if show_origin_image:
        origin_image.show()
    return text.strip()


def main():
    url = raw_input("Please input the url of captcha:\n > ").strip()
    print >> sys.stderr, ">>> Press Ctrl + C to stop."
    print >> sys.stderr, ">>> Press any key to continue."
    while True:
        raw_input()
        print distinguish_captcha(url)


if __name__ == "__main__":
    try:
        print main()
    except KeyboardInterrupt:
        print >> sys.stderr, ">>> Exit."
