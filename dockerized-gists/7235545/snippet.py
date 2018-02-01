#!/usr/bin/python

import sys
import datetime
import argparse

def is_queso_week(today=None):
    if today is None:
        today = datetime.datetime.now()
    if today.weekday() is not 0:
        bow = today - datetime.timedelta(today.weekday())
    else:
        bow = today
    while(bow.month == today.month):
        bow = bow - datetime.timedelta(7)
    valid_second_week = bow + datetime.timedelta(14)
    if today >= valid_second_week and today < (valid_second_week + datetime.timedelta(7)):
        return True
    else:
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', action='store_true', help="show all days in the year that fall in queso week")
    args = parser.parse_args()    
    if args.a:
        for m in range(1,13):
            for d in range(1,32):
                try: 
                    test_day = datetime.datetime(datetime.datetime.now().year, m, d)
                    print test_day, is_queso_week(test_day)
                except:
                    pass
    else:
        if is_queso_week(datetime.datetime.now()):
            print "Yep!"
        else:
            print "Nope"