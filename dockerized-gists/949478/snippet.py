# Can use this as an itty-bitty-frameworky-thing to manipulate CSV data from
# stdin and print a new csv to stdout, using tablib (http://tablib.org)
#
# Ex:
#    def csviscerator(data):
#        #do shit with tablib table!
#        return data
#
#    if __name__ == "__main__":
#        CSViscerate(csviscerator, headers=True)
#
# *shrug*

import re
from sys import stdin
import tablib
import csv

def CSViscerate(viscerator, **opts):
    # csv.reader and tablib aren't smart enough to read in numbers as numbers.
    # Therefore, I map this over the strings in the rows spat out by csv.reader.
    def str2num(string):
        if re.match('^-?\d*\.\d*$', string):
            return float(string)
        elif re.match('^-?\d+$', string):
            return int(string)
        else:
            return string


    # get raw data
    data = tablib.Dataset()
    for (no, row) in enumerate(csv.reader(stdin)):
        #Don't try this at home!
        try:
            if (opts['headers'] == True and no < 1):
                data.headers = row
            else:
                raise KeyError
        except KeyError:
            data.append( map(str2num, row) )

    #do something exciting with the data
    data = viscerator(data)
    try:
        if (type(opts['headers']) == type(list())):
            data.headers = opts['headers']
    except KeyError:
        pass

    print(data.csv)


def csviscerator(data):
    #do shit with tablib table!
    return data

if __name__ == "__main__":
    CSViscerate(csviscerator, headers=True)