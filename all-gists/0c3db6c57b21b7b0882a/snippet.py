#!/usr/bin/env python
from __future__ import print_function
import os
import subprocess as sp
import signal
import sqlite3
import sys
from os.path import expanduser
from time import sleep

if __name__ == '__main__':
    home = os.environ['HOME']
    conn = sqlite3.connect(sys.argv[1],
                        detect_types=sqlite3.PARSE_COLNAMES)
    c = conn.cursor()
    query = '''select a.item_artist,
                l.album,
                e.title,
                s.user_rating AS "rating [integer]"
                from item_stats s
                left join item i on i.item_pid = s.item_pid
                left join item_artist a on a.item_artist_pid = i.item_artist_pid
                left join item_extra e on e.item_pid = i.item_pid
                left join album l on l.album_pid = i.album_pid
                where i.item_pid is not null'''

    c.execute(query)

    data = []

    for row in c:
        artist = row[0]
        album = row[1]
        title = row[2]
        rating = row[3]

        data.append({
            'artist': artist,
            'album': album,
            'title': title,
            'rating': rating / 100
        })

    conn.close()

    # Kill any clementine instance
    try:
        pid = int(sp.check_output('pidof clementine', shell=True).strip())
        if pid:
            os.kill(pid, signal.SIGINT)
            sleep(2)  # let the clementine sub-processes quit
    except sp.CalledProcessError:
        pass

    clementine_db = expanduser('~/.config/Clementine/clementine.db')
    conn = sqlite3.connect(clementine_db)
    c = conn.cursor()

    for item in data:
        # title, album, artist, rating (float out of 1)
        t = info = (item['artist'], item['title'], item['album'])
        query = '''select title,album,artist
                    from songs where artist=?
                    and title=? and album=?'''

        c.execute(query, t)

        row = c.fetchone()

        if row is None:
            print('No song found for %s - %s - %s' % (info[0], info[1], info[2]), file=sys.stderr)
            continue

        query = 'UPDATE songs SET rating=? WHERE artist=? AND title=? AND album=?'
        t = (item['rating'], item['artist'], item['title'], item['album'])
        print('{} {}'.format(query, t), file=sys.stderr)

        c.execute(query, t)

    conn.commit()
    conn.close()
