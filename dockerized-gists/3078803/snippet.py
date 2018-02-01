from datetime import datetime
import calendar

def epoch_to_iso8601(timestamp):
    """
    epoch_to_iso8601 - convert the unix epoch time into a iso8601 formatted date

    >>> epoch_to_iso8601(1341866722)
    '2012-07-09T22:45:22'
    """
    return datetime.fromtimestamp(timestamp).isoformat()

def iso8601_to_epoch(datestring):
    """
    iso8601_to_epoch - convert the iso8601 date into the unix epoch time

    >>> iso8601_to_epoch("2012-07-09T22:27:50.272517")
    1341872870
    """
    return calendar.timegm(datetime.strptime(datestring, "%Y-%m-%dT%H:%M:%S.%f").timetuple())

if __name__ == "__main__":
    import doctest
    doctest.testmod()
