"""
This is a simple code to convert Moves JSON file to gpx files.
Each day in JSON file will be converted into different gpx file,
one file for a single day.
If you think this behavior annoying, please feel free to rewrite the code:D

Usage: 1. Get JSON file from: http://moves-export.herokuapp.com/
       2. The file you've got may have some errors to be a valid JSON file,
          so do some surgery to the file.
          I did `s/,\+/,/g`  in Vim to delete successive commas,
            and `s/}{/},{/g` to add a comma between braces.
       3. Feed the file to this code as an argument.
       4. You get .gpx files! (hopefully.)
"""

import argparse
import json
import datetime
from xml.dom.minidom import parseString

outputfilename = '{date}-moves-trackpoints.gpx'


# Prepare to convert Moves-style time format string.
timefmtstr = "%Y%m%dT%H%M%SZ"  # Could not use %Z, so I had to set tz myself.
class UTC(datetime.tzinfo):  # http://docs.python.org/2/library/datetime.html
    def utcoffset(self, dt): return datetime.timedelta(0)
    def tzname(self, dt): return "UTC"
    def dst(self, dt): return datetime.timedelta(0)
utc = UTC()
def strptime(timestr):
    return datetime.datetime.strptime(timestr, timefmtstr).replace(tzinfo=utc)


# A function to convert location to gpx trkpt string.
writetimefmtstr = "%FT%TZ"
def trkptstr(datetime_, lon, lat):
    timestr = datetime_.strftime(writetimefmtstr)
    writestr = '<trkpt lat="{lat}" lon="{lon}">'.format(lat=lat, lon=lon)
    writestr += '<time>{timestr}</time></trkpt>'.format(timestr=timestr)
    return writestr


def json2gpx(inputfile):
    # Load json file.
    locdata = json.loads(inputfile.read());  # If fail, check validity of json file.
    inputfile.close()

    # 2013-11-01 Moves Export service has changed its output form, so I had to add
    # the following line.
    locdata = locdata['export']

    # Dissolve the json file, and obtain all the lon-lat data.
    # Moves data format has several days in a huge single array.
    # Each item represents single day, so first of all,
    # create a loop in which only single day exists.
    for singleday in locdata:

        # Each day has "date" and "segements".
        # Here, we use "date" to create filename of GPX file.
        date = datetime.datetime.strptime(singleday['date'], '%Y%m%d')
        print('Processing: ' + date.strftime('%F'))

        # Prepare output string.
        outputstr = '<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n'
        outputstr += '<gpx xmlns="http://www.topografix.com/GPX/1/1"><trk><name>{date} Trackpoints from Moves Activity Tracker</name><trkseg>'.format(date=date.strftime("%F"))

        # We use "segments" to obtain location data.
        # each "segments" has several segment data, so create a loop for it.
        # Sometimes, segments is 'null', so look for it.
        if not singleday['segments']: continue
        for segment in singleday['segments']:

            # Segments have several "type"s. Each types contain a location info
            # in a different way, so make conditions of them.
            if segment['type'] == 'place':

                # "place" type has a single location info, and start & end time.
                # "place" has more infos than these, but I don't need them.
                # If you are interested, please read the json file you've got.
                starttime = strptime(segment['startTime'])
                endtime   = strptime(segment['endTime'])
                location  = segment['place']['location']
                lon, lat  = location['lon'], location['lat']
                assert type(lon)==float and type(lat)==float
                # print starttime, endtime, lon, lat  # for debug.
                outputstr += trkptstr(starttime, lon, lat)
                outputstr += trkptstr(endtime,   lon, lat)

            elif segment['type'] == 'move':

                # "move" type has "activities", which is an array of activities.
                # An activity has "trackPoints", which is an array of time and loc.
                for activity in segment['activities']:
                    for location in activity['trackPoints']:
                        time = strptime(location['time'])
                        lon, lat = location['lon'], location['lat']
                        assert type(lon)==float and type(lat)==float
                        # print time, lon, lat  # for debug.
                        outputstr += trkptstr(time, lon, lat)

        outputstr += '</trkseg></trk></gpx>'

        # Basically you don't need to prettify an xml, but just in case.
        outputstr = parseString(outputstr).toprettyxml(encoding="utf-8")

        # Export to a file.
        outputfile = open(outputfilename.format(date=date.strftime("%F")), 'w')
        outputfile.write(outputstr)
        outputfile.close()


if __name__ == '__main__':
    # create the parser
    parser = argparse.ArgumentParser(
        description='Convert Moves JSON file to gpx files.')
    parser.add_argument('inputfile', type=argparse.FileType('r'))
    args = parser.parse_args()

    json2gpx(args.inputfile)
