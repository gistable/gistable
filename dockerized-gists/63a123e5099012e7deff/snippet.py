#!/usr/bin/env python

from pytube import YouTube

VIDEOS = [
    # 'QuL6f5vmcWs',
    # '8u_6whomrCo',
    # 'kZwCF-LAnB8',
    # 'lCyhZezuY9Y',
    # 't8vnr18m_CI',
    # 'XiHwdry7rXw',
    # 'V7bPKFAv2y8',
    # '9uz98hOyZGE',
    # '9U2w4YOff5I',
    # 'yhn2cRuvZw8',
    # 'DmGZslmlLRQ',
    # 'yKGMiEGlKn4',
    # 'I8vzbIuvhoo',
    # '8k6GFR0II98',
    # 'PbTres_Q9Uw',
]

def main():
    """
    A script for downloading full episodes of SuperWhy from YouTube for airplane trips.
    Requirements:
    pip install -e git+git@github.com:NFicano/pytube.git#egg=pytube
    """

    for video in VIDEOS:
        yt = YouTube()
        yt.url = "https://www.youtube.com/watch?v=%s" % video
        v = yt.filter('mp4')[-1]
        v.download('videos/')

if __name__ == "__main__":
    main()