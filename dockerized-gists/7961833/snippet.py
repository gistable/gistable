"""
Simple algorithm to download all the egghead.io videos in highest-quality from YouTube.

Run from the directory you want the videos to appear. Renames them so that they have the video number + omit the repetitive "Egghead.io - AngularJS -" text.

Installing dependency:
$ pip install git+https://github.com/NFicano/pytube#egg=pytube
"""

from pytube import YouTube  #, exceptions as YTD_exceptions
from os.path import realpath

if __name__ == '__main__':
    uris = ('https://www.youtube.com/watch?v=Lx7ycjC8qjE', 'https://www.youtube.com/watch?v=MEmC0QH8ATQ',
            'https://www.youtube.com/watch?v=DTx23w4z6Kc', 'https://www.youtube.com/watch?v=HXpHV5gWgyk',
            'https://www.youtube.com/watch?v=Powr9vzqMac', 'https://www.youtube.com/watch?v=FX5TwV2ZKqc',
            'https://www.youtube.com/watch?v=wFYID8eYQLs', 'https://www.youtube.com/watch?v=bLohP9mh8ks',
            'https://www.youtube.com/watch?v=D4NyA-SFnZg', 'https://www.youtube.com/watch?v=xoIHkM4KpHM',
            'https://www.youtube.com/watch?v=AoDh1T_0Obg', 'https://www.youtube.com/watch?v=W82ztvDY_Po',
            'https://www.youtube.com/watch?v=IfUyUeYHffk', 'https://www.youtube.com/watch?v=LJmZaxuxlRc',
            'https://www.youtube.com/watch?v=rzMrBIVuxgM', 'https://www.youtube.com/watch?v=fYgdU7u2--g',
            'https://www.youtube.com/watch?v=7X5vx-n7Nxs', 'https://www.youtube.com/watch?v=O9iVkfQJauQ',
            'https://www.youtube.com/watch?v=mZGgNPTHc2Q', 'https://www.youtube.com/watch?v=97pv_kiYhv4',
            'http://egghead.io/lessons/angularjs-transclusion-basics', 'https://www.youtube.com/watch?v=L9-c2NvCuf4',
            'https://www.youtube.com/watch?v=bz-yhpaFElI', 'https://www.youtube.com/watch?v=JeuhhPlOZs0',
            'https://www.youtube.com/watch?v=_6ijcqI5fi8', 'https://www.youtube.com/watch?v=NnB2NBtoeAY',
            'https://www.youtube.com/watch?v=_23TfKY8If4', 'https://www.youtube.com/watch?v=boBm3AU-uX4',
            'https://www.youtube.com/watch?v=nZrbZ_sYShU', 'https://www.youtube.com/watch?v=TT31mYUEAPs',
            'https://www.youtube.com/watch?v=gNtnxRzXj8s', 'https://www.youtube.com/watch?v=T10gr1Leq6g',
            'https://www.youtube.com/watch?v=LGPXW-NgHCs', 'https://www.youtube.com/watch?v=o84ryzNp36Q',
            'https://www.youtube.com/watch?v=Kr1qZ8Ik9G8', 'https://www.youtube.com/watch?v=vIDvluer97A',
            'https://www.youtube.com/watch?v=rbqRJQZBF3Q', 'https://www.youtube.com/watch?v=-bv4Tp06Lxg',
            'https://www.youtube.com/watch?v=0uvAseNXDr0', 'https://www.youtube.com/watch?v=HvTZbQ_hUZY',
            'https://www.youtube.com/watch?v=OnSb4ebdjrk', 'https://www.youtube.com/watch?v=UCn7CwS5fKg',
            'https://www.youtube.com/watch?v=jEpbjve5iHk', 'https://www.youtube.com/watch?v=tTihyXaz4Bo',
            'https://www.youtube.com/watch?v=2CdivtU5ytY', 'https://www.youtube.com/watch?v=ZvWftlp7TKY',
            'https://www.youtube.com/watch?v=WX03ODuzkSY', 'https://www.youtube.com/watch?v=Bcv46xKJH98',
            'http://egghead.io/lessons/angularjs-animating-with-javascript', 'http://egghead.io/lessons/angularjs-animating-the-angular-way',
            # 50 ... currently goes all the way to 77 with no more on YouTube
            )

    uris_len = len(uris)
    for idx, uri in enumerate(uris):
        print 'Processing: {0:02d} / {1}\n({2})\n'.format(idx+1, uris_len, uri)
        
        if uri[12:19] != 'youtube':
            continue   # Not a YouTube link, but we still need idx incremented for filenames
        
        yt = YouTube()
        yt.url = uri
        yt.filename = '{0:02d}{1}'.format(idx, yt.filename[23:])

        video = None
        if not video:
            video = yt.get('mp4', '1440p')
        if not video:
            video = yt.get('mp4', '1080p')
        if not video:
            video = yt.get('mp4', '720p')
        #if not video:
        #    exit("Couldn't find high-quality download")

        if video:
            video.download(realpath(''))
