#!/usr/bin env python3
import re
import json
import os
import sys
import time
import signal
import urllib.request

opener = urllib.request.build_opener()

def sigint_handler(signal, frame):
    '''Handles ^c'''
    print('Recieved SIGINT! Exiting...')
    sys.exit(0)

def unescape(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace("&quot;", "\"")
    s = s.replace("&#8203;", " ") # How in the hell?
    s = s.replace("&amp;", "&") # This needs to be last
    return s

def get_list():
    cache = os.path.join('dew_music', 'music_list.json')
    try:
        os.mkdir('dew_music')
    except OSError:
        pass
    try:
        with open(cache, encoding='utf-8') as f:
            return json.loads(f.read())
    except IOError:
        with opener.open('https://docs.google.com/spreadsheet/pub?'
                         'key=0AhSz7tnijafVdFJBM1ZRQ2hBU1BtTXBkZWRVak1CelE&output=csv') as w:
            csv_data = w.read().decode('utf-8')
        music = dict()
        for i in csv_data.split('\n'):
            url, cat = i.split(',')
            cat = re.sub(r'\W', '', cat).lower()
            if cat not in music:
                music[cat] = [url]
            elif url not in music[cat]:
                music[cat].append(url)
        with open(cache, 'w') as f:
            f.write(json.dumps(music, indent=2))
        return music

def download_songs(url, category):
    try:
        with opener.open(url) as w:
            page = w.read().decode('utf-8')
    except urllib.error.HTTPError:
        print("404! Artist/Album may not exist! Skipping.")
        time.sleep(3)
        return 
    mp3s = re.findall(r'''"file":"(http:.*?)"''', page)
    titles = re.findall(r'''itemprop="url"><span itemprop="name">(.*?)</span>''', page)
    if not titles:
        titles = re.findall(r'''<h2 class="trackTitle" itemprop="name">\s*(.*?)\s*</h2>''', page)
    titles = [unescape(i) for i in titles]
    titles_clean = [re.sub(r'''\W''', '_', i) for i in titles]
    album = re.findall(r'''<title>(.*?) \|''', page)[0]
    album_clean = re.sub(r'''\W''', '_', album)
    artist = re.findall(r'''\| (.*?)</title>''', page)[0]
    artist_clean = re.sub(r'''\W''', '_', artist)
    base_path = os.path.join('dew_music', category, artist_clean, album_clean)
    sauce_path = os.path.join(base_path, 'sauce.txt')
    if os.path.isfile(sauce_path):
        print("{} by {} already downloaded! Skipping.".format(album, artist))
    else:
        print("Retrieving {} by {}.".format(album, artist))
        try:
            x = ''
            for y in base_path.split(os.sep):
                x = os.path.join(x, y)
                if not os.path.isdir(x):
                    os.mkdir(x)
        except OSError:
            pass
        for i, title in enumerate(titles_clean):
            mp3_path = os.path.join(base_path, "{:02d}_{}.mp3".format(i+1, title))
            print("Downloading {:02d} {}".format(i+1, titles[i]))
            if not mp3s:
                print("Music not free! Skipping.")
                break
            try:
                with opener.open(mp3s[i].replace('\\', '')) as w:
                    with open(mp3_path, 'wb') as f:
                        f.write(w.read())
            except urllib.error.HTTPError:
                print("404! Failed to download track! Skipping!")
                time.sleep(3)
                break
            except IndexError:
                print("Not all of this album is free! Making note in folder.")
                with open(os.path.join(base_path, 'WARNING.txt'), 'w') as f:
                    f.write("Warning, the track titles may be inaccurate for this album.\n"
                            "One or more songs may have been non-free!")
        with open(sauce_path, 'w') as f:
            f.write(url + '\n' + '\n'.join(["{:02d} {}".format(x+1, y)
                                             for x, y in enumerate(titles)]))

def main():
    args = sys.argv[1:]
    if args and args[0] == "--list":
        music = get_list()
        print("The list of categories to choose from are:")
        print(", ".join(music.keys()))
        print("You can specify multiple categories or 'all'.")
    elif args and args[0] == "--get" and len(args) >= 2:
        music = get_list()
        if 'all' in args[1:]:
            for x in music:
                for y in music[x]:
                    download_songs(y, x)
        else:
            for x in args[1:]:
                if x in music:
                    for y in music[x]:
                        download_songs(y, x)
                else:
                    print("{} is not a recognized category! Skipping.".format(x))
    else:
        print("Use --list to see the categories available and --get to download the music from"
               " said categories.\nWhen specifying categories, you can list multiple or 'all'.\n"
               "Sorry there's no tagging, I hope your media player can use the directory "
               "structure fot figure the tags out. A sauce.txt file is included along with every "
               "'album' which links to the source and includes the non-sanitized track names.\n"
               "This script supports very limited resuming in case of a failed download.")

if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_handler)
    main()
