# Depends on the OS X "say" command

import time, datetime, subprocess, math, sys

def say(s):
    subprocess.call(['say', str(s)])

def seconds_until(dt):
    return time.mktime(dt.timetuple()) - time.time()

def countdown_to(target_time, only_if_below=10, end_statement=None):
    said = set()
    while True:
        i = int(math.ceil(seconds_until(target_time)))
        if i < 0:
            if end_statement:
                say(end_statement)
            break
        if i <= only_if_below and i not in said:
            said.add(i)
            say(i)
        sys.stdout.write('%s. ' % i)
        sys.stdout.flush()
        time.sleep(0.1)

if __name__ == '__main__':
    countdown_to(
        datetime.datetime(2010, 1, 1, 0, 0, 0),
        10,
        'Happy new year!',
    )
