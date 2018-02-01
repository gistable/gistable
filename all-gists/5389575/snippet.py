#/usr/local/bin/python

"""Build Rescuetime Graph Data for StatusBoard.app

This script pulls data from a rescuetime account and flattens it into a format
that is easily read by StatusBoard. Okay. Run it with cron or launchd, whatever.

*nick wolfe
http://nameremoved.com/
"""

import csv
import json
import urllib2
import urllib
import time

base_url = "https://www.rescuetime.com/anapi/data/"
# To get the key for an interval, visit that page and request the Data API key
# eg for an hourly view
# https://www.rescuetime.com/browse/productivity/by/rank/for/the/day/of/2013-04-15
# Note that different intervals get different keys.
intervals = {
    'hour': {
        'key': 'YOUR_KEY_HERE',
        'format': '%H:%M'
    },
    'day': {
        'key': 'YOUR_KEY_HERE'
        'format': '%d %b'
    }
}
# This is where your output files live
output_folder = "/Users/YOUR_USERNAME_HERE/Dropbox/rt/"


def get_recent(name):
    """Query the rescuetime server for latest data"""
    query = urllib.urlencode({
        'key': intervals[name]['key'],
        'format': 'json',
        'perspective': 'interval',
        'resolution_time': name
    })
    try:
        return json.load(urllib2.urlopen(base_url + "?" + query))
    except ValueError:
        raise ValueError("Could not load data.")
    except urllib2.URLError:
        raise ValueError("Could not load data.")


def sort_times(data,):
    """Flatten the rescuetime data into a multicolumn view by interval

    key = (DATETIME, quality ranking)
    value = MINUTES (rounded down)
    """
    time_by_prod = {}
    for row in data['rows']:
        when, duration, who, quality = row
        when = time.strptime(when, "%Y-%m-%dT%H:%M:%S")
        time_by_prod[(when, quality)] = duration / 60
    return time_by_prod


def do_output(name, filetype):
    """Prepare the data and call the output function for the appropriate filetype"""
    time_by_prod = sort_times(get_recent(name))
    times = list(set(t[0] for t in time_by_prod.keys()))
    times.sort()
    filetypes[filetype]['output'](
        name,
        output_folder + name + filetypes[filetype]['ex'],
        time_by_prod,
        times
    )


def do_csv(name, outputfile, time_by_prod, times):
    """Flatten the data into a six-column CSV"""
    with open(outputfile, 'wb') as of:
        wr = csv.writer(of)
        wr.writerow([name, "VD", "D", "N", "P", "VP"])
        for when in times:
            row = [time.strftime(intervals[name]['format'], when)]
            for quality in [-2, -1, 0, 1, 2]:
                row.append(time_by_prod.get((when, quality), 0))
            wr.writerow(row)


def do_json(name, outputfile, time_by_prod, times):
    """Flatten the data into a JSON object"""
    graph = {"graph": {
        "title": name,
        "type": "bar",
        "datasequences": [{
            "title": "VD",
            "datapoints": []
        }, {
            "title": "D",
            "datapoints": []
        }, {
            "title": "N",
            "datapoints": []
        }, {
            "title": "P",
            "datapoints": []
        }, {
            "title": "VP",
            "datapoints": []
        }]
    }}
    for when in times:
        for i, quality in enumerate([-2, -1, 0, 1, 2]):
            graph["graph"]["datasequences"][i]["datapoints"].append({
                "title": time.strftime(intervals[name]['format'], when),
                "value": time_by_prod.get((when, quality), 0)
            })
    with open(outputfile, 'wb') as of:
        json.dump(graph, of)


filetypes = {
    'csv': {
        'ex': '.csv',
        'output': do_csv
    },
    'json': {
        'ex': '.json',
        'output': do_json
    }
}


def main():
    for filetype in filetypes:
        for interval in intervals:
            do_output(interval, filetype)


if __name__ == '__main__':
    main()
