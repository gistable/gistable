# 
# Script to retrieve magnetic declination data from www.ngdc.noaa.gov
# Retrieves specified latitude and longitude ranges (CONUS by default)
# and stores them in a cfg style text file
#
# Usage: Run script with no arguments, it will output declination.cfg
#        in the current directory
#
# Tested with Python 3.3.1
#
# Copyright (c) 2013 Kevan Ahlquist
#

import datetime
import re
import urllib.request
import urllib.parse
import xml.dom.minidom

# Change the following values for desired range
minLatitude = 24
maxLatitude = 50
minLongitude = -125
maxLongitude = -66
# ==============================================
latitudeRange = range(minLatitude, maxLatitude)
longitudeRange = range(minLongitude, maxLongitude)
recordsReceived = 0
totalRecords = abs((maxLatitude-minLatitude)*(maxLongitude-minLongitude))
percentDone = 0
print("Retrieving", totalRecords, "datapoints")

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)
    
print("Generating declination.cfg file...")
myFile = open('declination.cfg', 'w') # Delete current file, if it exists
myFile.close() 
myFile = open('declination.cfg', 'a') # Open new file in append mode

# Boilerplate info for config file
now = datetime.datetime.now()
month = now.month
dateString = now.strftime("%m/%d/%Y")
myFile.write('# Declination data from www.ngdc.noaa.gov\n')
myFile.write('# lat:%d-%d, long:%d-%d updated %s\n' % (minLatitude, maxLatitude, minLongitude, maxLongitude, dateString))
myFile.write('[declination]\n')

for latitude in latitudeRange:
    for longitude in longitudeRange:
        #encode URL parameters
        params = urllib.parse.urlencode({'lat1': latitude, 'lon1': longitude, 'resultFormat': 'xml', 'startMonth': month})
        #Load XML file
        f = urllib.request.urlopen("http://www.ngdc.noaa.gov/geomag-web/calculators/calculateDeclination?%s" % params)
        #Process XML file into object tree and get only declination info
        dom = xml.dom.minidom.parseString(f.read())
        myString = getText(dom.getElementsByTagName("declination")[0].childNodes)
        # At this point the string still contains some formatting, this removes it
        declination = str(re.findall(r"[-+]?\d*\.\d+|\d+", myString)[0])
        #Output formatting and append line to declination file
        if latitude > 0:
            latLabel = 'N'
        else:
            latLabel = 'S'
        if longitude > 0:
            longLabel = 'E'
        else:
            longLabel = 'W'
        myFile.write('%s%s%s%s=%s\n' % (latLabel, abs(latitude), longLabel, abs(longitude), declination))
        f.close()
        recordsReceived += 1
        if recordsReceived % 50 == 0:
            percentDone = float(recordsReceived) / float(totalRecords) * 100.0
            print("Progress:", int(percentDone), "%", end="\r")
print()
myFile.close()
