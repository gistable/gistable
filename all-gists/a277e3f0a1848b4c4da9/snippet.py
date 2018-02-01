import requests
import sqlite3
import os

# API key available at: http://trakt.tv/api-docs/authentication
API_KEY = "25665d450ed0c00907f32be617cd2a37"
TRAKT_USER = "nikolak"  # trakt username
TRAKT_URL = "http://api.trakt.tv/user/library/shows/all.json/{key}/{user}".format(
    key=API_KEY,
    user=TRAKT_USER)
IGNORED = ["Archer (1975)"]  # list of shows that will be ignored when adding
# absolute location where show folder will be created
SHOW_DIRECTORY = "/home/nikola/tv/series/"
# relative or absolute location of sickrage database file
DATABASE = "sickrage/sickbeard.db"

conn = sqlite3.connect(DATABASE)
c = conn.cursor()


def get_shows():
    r = requests.get(TRAKT_URL)
    if r.status_code != 200:
        print "Error getting data from trakt: HTTP status:", r.status_code
        return []
    else:
        return r.json()


def exec_query(tvdb_id, show_name, genres, imdb_id):
    print "Adding {} | {}".format(show_name, tvdb_id)
    show_path = os.path.join(SHOW_DIRECTORY, show_name)
    if not os.path.exists(show_path):
        os.makedirs(show_path)

    values = (None, tvdb_id, 1, show_name, show_path, '', '|' + '|'.join(genres) + '|',
              'Scripted', 0, 3, '', '', 0, 0, None, 0, 'en', 0, None, imdb_id, 0, 0, 0, '', '', 0, 0, 0)

    c.execute(
        "INSERT INTO tv_shows VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", values)

    pass


if __name__ == '__main__':
    all_shows = get_shows()
    for show in all_shows:
        query = c.execute('SELECT * FROM tv_shows WHERE show_name=?', (show['title'],)).fetchone():
        if show['title'] in IGNORED or not query:
            continue

        exec_query(
            show['tvdb_id'], show['title'], show['genres'], show['imdb_id'])

    if all_shows:
        conn.commit()
        conn.close()
        print "Changes saved to database"
    else:
        print "No changes made to database"
