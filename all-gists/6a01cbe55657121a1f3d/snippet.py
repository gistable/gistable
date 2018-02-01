# -*- coding: utf-8 -*-
"""
A tool for scrolling input text as ASCII art text banner in console
"""

import os
import time
from PIL import Image, ImageDraw, ImageFont


def init_console(cols, lines):
    os.system('mode con: cols=%s lines=%s' % (cols, lines))


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def get_text_size(font, text):
    return font.getsize(text)


def text_to_ascii_text(font, text, cols, lines):
    """Convert text to ASCII art text banner"""
    image = Image.new('RGB', (cols - 1, lines - 1), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, fill='black', font=font)
    width, height = image.size
    pixels = image.load()
    # convert image pixels to ASCII art
    out = ''
    for y in range(height):
        for x in range(width):
            pix = pixels[x, y]
            if pix != (255, 255, 255):
                out += '#'
            else:
                out += ' '
        out += '\n'
    return out


def main():
    """Main"""
    text = 'Scrolling ASCII text in console.'

    font = ImageFont.load_default()
    # font = ImageFont.truetype('arial.ttf', 16)

    # get size of space char
    space_width = get_text_size(font, ' ')[0]

    # get size of text
    text_height = get_text_size(font, text)[1]

    # resize console
    cols = 100
    lines = int(text_height * 1.25)
    init_console(cols, lines)

    # add some padding to the text
    padding = ' ' * int(cols / space_width + 1)
    text = padding + text

    index = 0
    try:
        while True:
            clear_console()
            print(text_to_ascii_text(font, text[index:], cols, lines))
            index += 1
            if index > len(text):
                index = 0
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
