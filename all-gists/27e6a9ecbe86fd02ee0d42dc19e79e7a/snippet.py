import csv
import sys
import calendar
import time
from datetime import datetime

# /storage/emulated/0/sleep-data/sleep-export.csv
# Formates Date/Time objects in Sleep as Android format
def sleepandroid_time(time):
    return '%.2d. %.2d. %d %d:%.2d' % (time.day, time.month, time.year, time.hour, time.minute)

def parse_row(row):
    frm = datetime.strptime(row[0] + " " + row[1], "%m/%d/%y %H:%M")
    to = datetime.strptime(row[0] + " " + row[2], "%m/%d/%y %H:%M")
    hours = float(row[3])
    return (frm, to, hours)

def main():
    reader = csv.reader(open(sys.argv[1]))
    # writer = csv.writer(open(sys.argv[2], "wb"))
    writer = csv.writer(sys.stdout, lineterminator='\n')
    for i, row in enumerate(reader):
        if i > 0:
            frm, to, hours = parse_row(row) 

            frm_timestamp = time.mktime(frm.timetuple())
            ID = int(frm_timestamp) * 1000

            writer.writerow(['Id', 'Tz', 'From', 'To',
                             'Sched', 'Hours', 'Rating', 'Comment',
                             'Framerate', 'Snore', 'Noise',
                             'Cycles', 'DeepSleep', 'LenAdjust',
                             'Geo', '%d:%d' % (to.hour, to.minute),
                             'Event', 'Event'])
            writer.writerow([ID, "Asia/Tokyo", sleepandroid_time(frm), sleepandroid_time(to),
                             sleepandroid_time(to), str(hours), "0", "",
                             "10000", "-1", "-1",
                             "-1", "-1", 0, 
                             "", "0",
                             "DEEP_START-" + str(int(frm_timestamp) * 1000), "DEEP_END-" + str(int(frm_timestamp) * 1000)])


if __name__ == '__main__':
    main()