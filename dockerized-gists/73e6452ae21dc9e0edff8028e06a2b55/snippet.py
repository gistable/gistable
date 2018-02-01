import requests
import subprocess
from time import sleep
from random import randrange
from datetime import datetime


i = 0
def get_content():
    global i
    r = requests.get('http://www.zio.iiar.pwr.wroc.pl/pea/?C=M;O=D')
    print(i, datetime.now(), r)
    i += 1
    return r.text


def main():
    t = get_content()
    while 1:
        sleep(30 + randrange(30))
        t2 = get_content()
        if t2 != t:
            break

    subprocess.check_output(['vlc', 'music.mp3'])


if __name__ == '__main__':
    main()