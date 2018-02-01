"""
iphone_gps.py
When fed exif data from an image taken with an iPhone, this script will
open a browser to the coordinates where the image was taken.

Usage:
$ exiftool image.jpg | python ./iphone_gps.py
"""
import re
import fileinput
import os

url_template = "https://www.google.com/maps/place/find+{LAT},{LONG}"
latitude = 0.0
longitude = 0.0
pattern = re.compile(r"[-+]?\d*\.\d+|\d+")


def to_decimal(arr):
    degrees = float(arr[0])
    minutes = float(arr[1])
    seconds = float(arr[2])
    return float(degrees + (minutes/60) + (seconds/3600))

for line in fileinput.input():
    if re.match("GPS Latitude\s{4,}", line):
        digits = re.findall(pattern, line)
        latitude = to_decimal(digits)
        if re.match(".*S$", line):  # If South, make negative
            latitude = -latitude
    if re.match("GPS Longitude\s{4,}", line):
        digits = re.findall(pattern, line)
        longitude = to_decimal(digits)
        if re.match(".*W$", line):  # If West, make negative
            longitude = -longitude

url_template = url_template.format(LAT=latitude, LONG=longitude)
os.system("open {URL}".format(URL=url_template))
