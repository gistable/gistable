#!/usr/local/bin/python3
# Make a new reminder via terminal script
# args: remind <title> <date> <time>
# example: remind clean 12/10/2012 10:00:00PM
import subprocess
import sys
from datetime import datetime, timedelta

# A apple script that creates a new reminder given a name date and time 
OSASCRIPT = ('<<END\n'
'on run argv\n'
'    set dateString to date (item 2 of argv & " " & item 3 of argv)\n'
'    tell application "Reminders"\n'
'        make new reminder with properties {name:item 1 of argv, due date:dateString}\n'
'    end tell\n'
'end run\n'
'END')

def parse_time_arg(time_arg):
    formats = ['%H:%M', '%H']
    for format in formats:
        try:
            t = datetime.strptime(time_arg, format)
            break
        except ValueError:
            pass
    else:
        print("Incorrect time formatting")
        exit(1)
    return t

def parse_date_arg(date_arg):
    td = datetime.today()    
    if date_arg == "today":
        d = td
    elif date_arg == "tomorrow":
        d = td + timedelta(days=1)
    else:
        formats = ["%m/%d/%y", "%m/%d", "%m%d"]
        for format in formats:
            try:
                d = datetime.strptime(date_arg, format)
                break
            except ValueError:
                pass
        else:
            print("Incorrect date formatting")
            exit(1)
        # An empty year argument defaults to 1900
        if d.year == 1900:
            # Find the nearest year that can fall possibly contain 
            # the inputted date.
            if d.month < td.month:
                closest_year = td.year+1
            else:
                closest_year = td.year
            d = d.reaplace(year=closest_year)
    return d    

def new_reminder(remind_datetime, name):
    timestr = remind_datetime.strftime("%I:%M:00%p")
    datestr = remind_datetime.strftime("%m/%d/%Y")
    # Execute applescript via shell to create a new reminder.
    command = 'osascript - "{n}" {d} {t} {osa}'.format(n=name, d=datestr, 
                                                       t=timestr, osa=OSASCRIPT)
    with open('/dev/null', 'w') as devnull:
        status = subprocess.call(command, shell=True, stdout=devnull)
    return status

def main():
    name, date_arg, time_arg = sys.argv[1:4]

    t = parse_time_arg(time_arg)
    d = parse_date_arg(date_arg)
    dt = t.replace(day=d.day, month=d.month, year=d.year)

    status = new_reminder(dt, name)

    if status == 0:
        print("New Reminder:\n"
              "{0}: {1}".format(dt.strftime("%m/%d/%Y %H:%M"), name))
    else:
        print("Error occured")

if __name__ == "__main__":
    main()
