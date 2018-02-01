"""
auth_parser.py by Christopher Wahl of nothingmuch.net

A simple script to pull some information out of a server's auth.log file regarding invalid user login attempts via SSH.
Infographic of data collected from 10 Oct to 31 Oct 2017 available here: 
https://www.nothingmuch.net/post/15/three-weeks-of-bots-trying-to-login-to-my-ssh-serv.html

This was written on Python 3.6, but it should be compatible with any Python 3 versions the packages below are available for.

Will need the packages:
  pytz, tzwhere, maxminddb-geolite2, python-dateutil
from pip, and the dependencies they come along with.


Sample line from auth.log:
Oct 25 23:59:18 myhostname sshd[4543]: Invalid user bob from 127.0.0.1
"""

from ipaddress import ip_address

from dateutil import parser
from geolite2 import geolite2
from pytz import UTC, timezone
from tzwhere import tzwhere

# Note the leading space here.  It's important for using this
# to split the log line in the proper place.
HOSTNAME = " myhostname"
LOGFILE = 'auth.log'

# Utilities for looking up countries of origin given an IP
# and establishing the local time.
# Will use forceTZ to set any unknown sources to UTC timezone
READER = geolite2.reader()
FINDER = tzwhere.tzwhere(forceTZ=True).tzNameAt


def readlogfile() -> None:
    """
    Read in the log file, get the data, write it to the disk

    :return: None
    """
    from collections import defaultdict

    # Dictionaries which will initialize any new key to a value of 0.
    users = defaultdict(int)
    countries = defaultdict(int)
    weekdays = defaultdict(int)
    days = defaultdict(int)
    hours = defaultdict(int)

    print("Parsing '{}'... ".format(LOGFILE), end="", flush=True)
    with open(LOGFILE, 'r') as infile:
        i = 0
        for line in infile:
            if 'Invalid user' in line:
                i += 1
                user, country, date = breakdown_line(line)

                # iterate the counters
                users[user] += 1
                countries[country] += 1
                days[date.day] += 1
                weekdays[date.weekday()] += 1
                hours[date.hour] += 1
    print("{} value{} found.".format(i, "s" if i != 1 else ""), end="\n")
    print("\n\tUnique usernames:\t{}".format(len(users)))
    print("\tUnique countries:\t{}".format(len(countries)))

    print("\n  ------------")
    print("Writing CSVs...", end="", flush=True)
    simplewriter(users, 'users')
    simplewriter(countries, 'countries')
    simplewriter(days, 'days')
    simplewriter(weekdays, 'weekdays')
    simplewriter(hours, 'hours')
    print("Done", end="\n")


def breakdown_line(line: str) -> tuple:
    """
    Breaks down the log line, assuming said line contains 'Invalid user '

    :type line: str
    :rtype: tuple
    """
    line = line.strip()

    # Using the sample line above, breaks up the line into:
    #       date = Oct 25 23:59:18
    #   and
    #       line = sshd[4543]: Invalid user bob from 127.0.0.1, then to:
    #       line = bob from 127.0.0.1
    date, line = line.split(HOSTNAME)
    line = line.split('Invalid user ')[1]  # Note the trailing space

    # Turn the date string a datetime object
    # My server logs in UTC.  The extra formatting simplfies adding in the
    # local timezone and year, since
    #   Oct 25 23:59:18
    # doesn't include those objects
    date = parser.parse('{} UTC 2017'.format(date))

    # Get the final username string, and get the IP address
    # username = 'bob'
    # ip = 127.0.0.1
    username, ip = line.split(' from ')
    ip = ip_address(ip)

    # Query the DB for IP info.  There's A LOT more info in here than I used.
    request = READER.get(ip)
    try:
        country = request['country']['names']['en']

        try:
            tz = timezone(request['location']['time_zone'])
        except KeyError:
            # Can't find a timezone from the given country (perhaps nonstandard name?)
            # Use the lat/lon of the request instead.
            lat = request['location']['latitude']
            lon = request['location']['longitude']
            tz = timezone(FINDER(lat, lon, True))
    except (KeyError, TypeError):
        # Can't find a country and can't find a timezone from the lat/lon given
        # so just set it to UTC and 'Unknown'
        country = 'Unknown'
        tz = UTC

    # Convert the server date/time to the origin date/time
    date = date.astimezone(tz)

    return username, country, date


def simplewriter(d: dict, filename: str) -> None:
    """
    Writes a simple dictionary to CSV

    :type d: dict
    :type filename: str
    :return: None
    """
    if not filename.endswith('.csv'):
        filename += '.csv'
    with open(filename, 'w') as outfile:
        outfile.writelines("{},{}\n".format(key, value) for key, value in d.items())


if __name__ == '__main__':
    readlogfile()
