#!/usr/bin/env python
# coding: utf-8

#for encode: pip install qrcode
import qrcode

#for decode: pip install zbar  
#如果报找不到zbar.h,则先安装libzbar-dev
import zbar

import Image


def encodeQR(data, qrPath='qr.png'):
    # 简洁用法
    # img = qrcode.make(data)
    # img.save(qrPath)

    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make()
    img = qr.make_image(fit=True)
    img.save(qrPath)



def decodeQR(qrPath='qr.png'):
    scanner = zbar.ImageScanner()
    scanner.parse_config('enable')

    pil = Image.open(qrPath).convert('L')
    width, height = pil.size

    raw = pil.tostring()

    image = zbar.Image(width, height, 'Y800', raw)

    scanner.scan(image)

    data = {}

    for symbol in image:
        #print type(symbol.type) #<type 'zbar.EnumItem'>
        data[str(symbol.type)] = symbol.data

    del(image)
    return data



encodeQR('hello')
print decodeQR()