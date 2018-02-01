import requests
import re
import sys
import time
import json
import sqlite3
from websocket import create_connection, WebSocket


colors = [
    "#FFFFFF",
    "#E4E4E4",
    "#888888",
    "#222222",
    "#FFA7D1",
    "#E50000",
    "#E59500",
    "#A06A42",
    "#E5D900",
    "#94E044",
    "#02BE01",
    "#00D3DD",
    "#0083C7",
    "#0000EA",
    "#CF6EE4",
    "#820080"
]


class PlaceWebSocket(WebSocket):
    def recv_frame(self):
        frame = super().recv_frame()
        return json.loads(frame.data.decode('utf-8'))


def db_connect(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute(
    '''CREATE TABLE IF NOT EXISTS placements (
        recieved_on INTEGER,
        y INTEGER,
        x INTEGER,
        color INTEGER,
        author TEXT
    )''')
    c.execute(
    '''CREATE TABLE IF NOT EXISTS activity (
        recieved_on INTEGER,
        count INTEGER
    )''')
    c.execute(
    '''CREATE TABLE IF NOT EXISTS starting_bitmaps (
        recieved_on INTEGER,
        data BLOB
    )''')
    c.execute('CREATE INDEX IF NOT EXISTS placements_recieved_on_idx ON placements (recieved_on)')
    c.execute('CREATE INDEX IF NOT EXISTS placements_author_idx ON placements (author)')
    c.execute('CREATE INDEX IF NOT EXISTS placements_color_idx ON placements (color)')
    c.execute('CREATE INDEX IF NOT EXISTS activity_recieved_on_idx ON activity (recieved_on)')
    conn.commit()

    return c, conn


def save_bitmap(c, conn):
    resp = requests.get('https://www.reddit.com/api/place/board-bitmap')
    c.execute('''INSERT INTO starting_bitmaps VALUES (?, ?)''', [
        int(time.time()),
        resp.content
    ])
    conn.commit()


def get_place_url():
    match = None

    while match is None:
        resp = requests.get('https://reddit.com/r/place')
        url_re = re.compile(r'"place_websocket_url": "([^,]+)"')  # Forgive me, for I am a sinner
        matches = re.findall(url_re, resp.content.decode('utf-8'))

        if len(matches) > 0:
            match = matches[0]

    return match


def main():
    url = get_place_url()
    ws = create_connection(url, class_=PlaceWebSocket)
    c, conn = db_connect('place.sqlite')
    save_bitmap(c, conn)
    insert_queue = 0
    inserted_count = 0
    max_queue_size = 100
    save_frame_per = 20000

    while True:
        try:
            frame = ws.recv_frame()
            print(frame)

            if frame['type'] == 'place':
                c.execute('''INSERT INTO placements VALUES (?, ?, ?, ?, ?)''', [
                    int(time.time()),
                    frame['payload']['x'],
                    frame['payload']['y'],
                    frame['payload']['color'],
                    frame['payload']['author']
                ])
                insert_queue += 1
                inserted_count += 1
            elif frame['type'] == 'activity':
                c.execute('''INSERT INTO activity VALUES (?, ?)''', [
                    int(time.time()),
                    frame['payload']['count']
                ])
                insert_queue += 1
                inserted_count += 1

            if insert_queue >= max_queue_size:
                conn.commit()
                insert_queue = 0
            if inserted_count % save_frame_per == 0:
                save_bitmap(c, conn)
        except KeyboardInterrupt:
            print('Exiting safely...')
            conn.commit()
            conn.close()
            sys.exit()
        except Exception as e:
            print('Error occured: {}'.format(str(e)))


if __name__ == '__main__':
    main()
