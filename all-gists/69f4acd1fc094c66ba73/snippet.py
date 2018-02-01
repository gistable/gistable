#!/usr/bin/env python3

import time

import cron

def do_stuff1():
    print('stuff1!')
def do_stuff2():
    #1 / 0
    print('stuff2!')

cron.init()
cron.schedule(5, do_stuff1)
#time.sleep(1)
#cron.schedule(2, do_stuff2)
cron.wait()
print('done!')