import sys
import urllib
import json
from pyechonest import playlist


def show_playlist(seed_artist):
    for s in playlist.basic(artist=seed_artist, type='artist-radio', ]
                buckets=['id:lyricfind-US'], results=10, limit=True):
        print '=================================================================='
        print s.title, 'by', s.artist_name
        print '=================================================================='
        show_lyrics(s)


def show_lyrics(s):
    lfid = s.get_foreign_id('lyricfind-US').replace('lyricfind-US:song:', '')
    url = 'http://test.lyricfind.com/api_service/lyric.do' +  \
        '?apikey=your_api_key' + \
        '&reqtype=default&output=json&trackid=elid:' + lfid
    f = urllib.urlopen(url)
    js = f.read()
    f.close()
    dict = json.loads(js)

    try:
        lyrics = dict['track']['lyrics']
        for line in lyrics.split('\r\n'):
            print line
        print
    except:
        print '(no lyrics)'


if __name__ == '__main__':
    if len(sys.argv) > 1:
        show_playlist(' '.join(sys.argv[1:]))
    else:
        print 'usage: %s artist name' % (sys.argv[0],)