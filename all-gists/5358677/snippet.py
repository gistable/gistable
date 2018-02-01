# -*- coding: utf-8 -*-

import alfred
import calendar
import time
import math
from delorean import utcnow, parse, epoch

# global var to see if user
# has a time offset
_offset = 0

def process(query_str):
    """ Entry point """
    value = parse_query_value(query_str)
    if value is not None:
        results = alfred_items_for_value(value)
        xml = alfred.xml(results) # compiles the XML answer
        alfred.write(xml) # writes the XML back to Alfred

def parse_query_value(query_str):
    """ Return value for the query string """
    try:
        query_str = str(query_str).strip('"\' ')

        if query_str == 'now':
            d = utcnow()

        elif query_str.startswith('tz'):
            global _offset
            # get correction for local time and DST
            _offset = local_time_offset()
            # get current time
            epoch_time = time.time()
            # create delorean with local time 
            d = epoch(float(epoch_time+_offset))
        else:
            # Parse datetime string or timestamp
            try:
                d = epoch(float(query_str))
            except ValueError:
                d = parse(str(query_str))
    except (TypeError, ValueError):
        d = None
    return d

def local_time_offset(t=None):
    """Return offset of local zone from GMT, either at present or at time t."""
    # python2.3 localtime() can't take None
    if t is None:
        t = time.time()

    if time.localtime(t).tm_isdst and time.daylight:
        return -time.altzone
    else:
        return -time.timezone

def construct_offset_string():
    global _offset

    # round to the nearest minute by adding 30 seconds
    # then take the floor of 60, then multiply again by 60
    # to get back to seconds, just in case
    _offset = int((_offset + 30) // 60) * 60 

    # convert to hours, round to 1 dp
    _offset = round((float(float(_offset) / float(3600))),1)
    
    # save the sign
    # using a ternary-like conditional
    # added in Python 2.5 http://cloud.zoooot.com/OCLx
    # so all Alfred 2 users should be on 2.5+
    sign = "-" if _offset < 0 else "+"

    # check for half hour timezones
    if math.fmod(_offset, 1) != 0:
        # convert FLOAT to string
        offsetStr = str(math.fabs(_offset))
    else:
        # convert to INT then a string
        offsetStr = str(int(abs(_offset)))

    #if length is 1, we add a zero in front and 2 after
    if len(offsetStr) == 1:
        offsetStr = "0" + offsetStr + ":00"
    elif len(offsetStr) == 2:
        #else just 2 after - still a whole hour
        offsetStr = offsetStr + ":00"
    elif len(offsetStr) == 3:
        #half hour single digit
        # reuse the offset
        offsetStr = "0" + str(int(abs(_offset))) + ":30"
    elif len(offsetStr) == 4:
        #half hour double digit
        offsetStr = str(int(abs(_offset))) + ":30"

    # add the sign back on
    offsetStr = sign + offsetStr

    return offsetStr

def alfred_items_for_value(value):
    """
    Given a delorean datetime object, return a list of
    alfred items for each of the results
    """
    subtitleStr=u'UTC Timestamp'

    if _offset != 0:
        tmpStr = construct_offset_string()
        subtitleStr=u'UTC' + tmpStr + u' Timestamp'

    index = 0
    results = []

    # First item as timestamp
    item_value = calendar.timegm(value.datetime.utctimetuple())
    results.append(alfred.Item(
        title=str(item_value),
        subtitle=subtitleStr,
        attributes={
            'uid': alfred.uid(index), 
            'arg': item_value,
        },
        icon='icon.png',
    ))
    index += 1

    # Various formats
    formats = [
        # 1937-01-01 12:00:27
        ("%Y-%m-%d %H:%M:%S", ''),
        # 19 May 2002 15:21:36
        ("%d %b %Y %H:%M:%S", ''), 
        # Sun, 19 May 2002 15:21:36
        ("%a, %d %b %Y %H:%M:%S", ''), 
        # 1937-01-01T12:00:27
        ("%Y-%m-%dT%H:%M:%S", ''),
        # 1996-12-19T16:39:57-0800
        ("%Y-%m-%dT%H:%M:%S%z", ''),
    ]
    for format, description in formats:
        item_value = value.datetime.strftime(format)
        results.append(alfred.Item(
            title=str(item_value),
            subtitle=description,
            attributes={
                'uid': alfred.uid(index), 
                'arg': item_value,
            },
        icon='icon.png',
        ))
        index += 1

    return results

if __name__ == "__main__":
    try:
        query_str = alfred.args()[0]
    except IndexError:
        query_str = None
    process(query_str)
