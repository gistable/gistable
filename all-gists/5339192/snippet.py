#!/usr/bin/python2

import datetime
import subprocess
import sys
import time

start_date=datetime.date(2012,11,1)
end_date = datetime.date(2013, 04, 9)

series_data = {}

for n in range(int ((end_date - start_date).days)):
    dte = start_date + datetime.timedelta(n)
    series_data[time.strftime("%Y%m%d", dte.timetuple())] = 0

    
def exec_cmd(cmd):
    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               stdin=subprocess.PIPE,
                               stderr=subprocess.PIPE
                           )
    (out, err) = process.communicate()
    return (process.returncode, out, err)
    

SMS_DB="/data/data/com.android.providers.telephony/databases/mmssms.db"

adb_cmd = ["adb",
           "shell"]

def update_dataset(data):
    dataset = {}
    for row in data:
        s = row.split("|")
        if len(s) == 2:
            k, v = s
            dataset[k] = int(v.replace("\r",""))
            
    return dataset


def to_csv():
    for k in series_data:
        print "%s,%s" % (k, series_data[k])


def sms_trend_by_date(outgoing=False):
    cond = ' where type = 1 ' if not outgoing else ' where type = 2 '
    query = 'SELECT strftime("%s", datetime(date/1000,"unixepoch", "localtime")) dte, count(_id) FROM sms %s group by dte order by dte' % ("%Y%m%d", cond)
    cmd = adb_cmd + ['sqlite3 %s "%s"' %(SMS_DB, query.replace('"', r'\"'))]
    rc, out, err = exec_cmd(cmd)

    if not rc:
        dataset = update_dataset(out.split("\n"))
        series_data.update(dataset)
        to_csv()
    else:
        print "Not OK"


def main():
    if len(sys.argv) == 2 and sys.argv[1].lower() == 'out':
        sms_trend_by_date(True)
    else:
        sms_trend_by_date(False)    


if __name__ == "__main__":
    main()
