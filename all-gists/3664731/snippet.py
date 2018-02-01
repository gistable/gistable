#!/usr/bin/env python
import netrc, urllib, urllib2
from gmusicapi.api import Api
from xml.etree.ElementTree import *

lastfm__user = 'oquno'
api_key = 'your apikey'

def init():
    api = Api()
    (email, account, password) = netrc.netrc().hosts['google.com']
    logged_in = api.login(email, password)
    if not logged_in:
        api = None
    return api

def get_loved():
    loved = []
    page = 1
    while True:
        url = 'http://ws.audioscrobbler.com/2.0/?method=user.getlovedtracks&user=%s&api_key=%s&page=%d'
        url = url % (lastfm_user, api_key, page)
        tree = parse(urllib2.urlopen(url)).getroot()
        tracks = tree.findall('lovedtracks/track')
        for track in tracks:
            title = track.find('name').text
            artist = track.find('artist/name').text
            loved.append([artist,title])
        if not len(tracks) == 50:
            break
        page+=1
    return loved

def main():
    api = init()
    if api == None:
        print 'login error'
        return

    loved = get_loved()
    if len(loved) == 0:
        print 'no loved tracks'
        return

    songs = api.get_all_songs()
    if len(songs) == 0:
        print 'no songs in library'
        return

    favs = []
    for song in songs:
        if [song['artist'], song['name']] in loved:
                song['rating'] = 5
                print '☝: %s - %s' % (song['artist'], song['name'])
                favs.append(song)
    api.change_song_metadata(favs) 

if __name__ == '__main__':
    main() 