#!/usr/bin/python -tt

"""
Takes an screenshot (the user draws a rectangle to select the interesting area), scans the resulting image and copy the text to clipboard

- scrot (http://en.wikipedia.org/wiki/Scrot)
- readbot (`pip install readbot`)
- pyperclip (`pip install pyperclip`)
"""

import sys
import subprocess
import pyperclip
from readbot import ReadBot

TEMPORARY_FILENAME = "/tmp/ocr_screenshot.png"


def grab_screenshot():
    """
    Takes an screenshot and returns the saved file path
    """

    try:
        retcode = subprocess.call('scrot -s ' + TEMPORARY_FILENAME, shell=True)
        if retcode == 0:
            return TEMPORARY_FILENAME
    except OSError as e:
        sys.stderr.write('Execution failed: ' + e)


def image_to_clipboard(img_path):
    """
    Given an screenshot copy text to clipboard
    """

    if img_path:
        rb = ReadBot()
        text = rb.interpret(img_path)
        if text:
            pyperclip.copy(text)
    else:
        sys.stderr.write('No screenshot supplied')


if __name__ == '__main__':
    image_to_clipboard(grab_screenshot())
