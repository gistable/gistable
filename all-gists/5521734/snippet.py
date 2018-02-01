"""
Extract GPS coordinates and filename, output to CSV file
Run this file from the same directory the images are in
run using ./process_exif.py or python process_exif.py, or
%run process_exif.py from an IPython instance

Ensure you have PIL installed
refer to http://www.exiv2.org/tags.html for a full detailed tag listing

This is what the GPSInfo dict looks like for an iPhone 5 jpg:

{
    1: 'N', # latitude ref
    2: ((51, 1), (3154, 100), (0, 1)), # latitude, rational degrees, mins, secs
    3: 'W', # longitude ref
    4: ((0, 1), (755, 100), (0, 1)), # longitude rational degrees, mins, secs
    5: 0, # altitude ref: 0 = above sea level, 1 = below sea level
    6: (25241, 397), # altitude, expressed as a rational number
    7: ((12, 1), (16, 1), (3247, 100)), # UTC timestamp, rational H, M, S
    16: 'T', # image direction when captured, T = true, M = magnetic
    17: (145423, 418) # image direction in degrees, rational
}

"""

import sys
import ntpath
import glob
from itertools import chain
from PIL.ExifTags import TAGS
from PIL import Image
import csv
from datetime import datetime as dt


def multiple_file_types(*patterns):
    """ get around Python's lack of regex support in glob/iglob """
    return chain.from_iterable(glob.iglob(pattern) for pattern in patterns)


def path_leaf(path):
    """ guaranteed filename from path; works on Win / OSX / *nix """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def latlon(path):
    """
    returns a dict of lat, lon, alt, filename values, given
    an input file path as string
    example: latlong("path/to/file") or latlon(variable)
    """
    img = Image.open(path)
    info = img._getexif()
    filename = path_leaf(path)
    # build a dict of decoded exif keys and values
    decoded = dict((TAGS.get(key, key), value) for key, value in info.items())
    info = {
        "filename": filename,
        "lat": None,
        "lon": None,
        "timestamp": None,
        "altitude": None,
    }
    # ensure that this photo contains GPS data, or return an empty dict:
    if not decoded.get('GPSInfo'):
        return info
    lat = [float(x) / float(y) for x, y in decoded['GPSInfo'][2]]
    lon = [float(x) / float(y) for x, y in decoded['GPSInfo'][4]]
    alt = float(decoded['GPSInfo'][6][0]) / float(decoded['GPSInfo'][6][1])
    timestamp = decoded['DateTimeOriginal']
    # assign values to dict
    info['filename'] = filename
    info['lat'] = (lat[0] + lat[1] / 60)
    info['lon'] = (lon[0] + lon[1] / 60)
    info['timestamp'] = dt.strptime(
        timestamp,
        "%Y:%m:%d %H:%M:%S").strftime("%Y/%m/%d %H:%M:%S")
    info['altitude'] = alt
    # corrections if necessary
    if decoded['GPSInfo'][1] == "S":
        info['lat'] *= -1
    if decoded['GPSInfo'][3] == "W":
        info['lon'] *= -1
    # if we're below sea level, the value's negative
    if decoded['GPSInfo'][5] == 1:
        info['altitude'] *= -1
    return info


def write_csv():
    """ coroutine for writing dicts to a CSV as rows """
    header_written = False
    # create a CSV writer object
    with open("fileinfo.csv", "w") as f:
        while True:
            data = (yield)
            # don't bother writing anything unless we have GPS data
            if data['lat']:
                dw = csv.DictWriter(f, sorted(data.keys()))
                if not header_written:
                    dw.writeheader()
                    header_written = True
                dw.writerow(data)

"""
Step 1 is a generator of all files matching the jpg/JPG/JPEG/jpeg pattern
Step 2 attempts to extract Exif GPS data from the file, and returns a dict
Step 3 is a coroutine, writing the dict to a CSV row if it contains GPS data
"""
# create a generator of all jpg files in the current dir
print("Getting a list of all jpg files in the current dir...")
# let's be absolutely sure we're getting everything that looks like a jpg
images = multiple_file_types("*.jpg", "*.JPG", "*.jpeg", "*.JPEG")
try:
    # initialise a CSV writer coroutine
    output = write_csv()
    output.next()
    # pipe each GPS-data-containing dict from the generator to the CSV writer
    print("writing to CSV...")
    [output.send(data) for data in (latlon(image) for image in images)]
except IOError:
    print(
        """
        There was a read/write error. Ensure that you have read and write
        permissions for the current directory
        """
    )
    sys.exit(1)
print("And we're done.")
output.close()
