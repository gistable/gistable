#!/usr/bin/env python
import argparse
import errno
import itertools
import json
import os
import requests
import time

WIDTHS = (1280, 500, 400, 250, 100, 75)
REQUEST_URL = 'http://%s.tumblr.com/api/read/json?debug=1&start=%d'

def download_photo(blog, pid, photo, p):
    for width in WIDTHS:
        photo_size = 'photo-url-%d' % width
        if photo_size in photo:
            print 'downloading photo %d @ %spx' % (p, width)
            photo_url = photo[photo_size]
            photoreq = requests.get(photo_url,
                                 stream=True)
            photoreq.raise_for_status()
            with open(os.path.join(blog, '%s.%s%s' % (pid, p,
                    os.path.splitext(photo_url)[1])), 'wb') as out:
                for chunk in photoreq.iter_content(1024):
                    out.write(chunk)
            return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=int, default=0,
                        help='the starting offset')
    parser.add_argument('blog', help='the blog to backup')
    args = parser.parse_args()
    
    blog = args.blog
    start = args.start
    
    # Make a directory for the images
    try:
        os.mkdir(blog)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(blog):
            pass
        else:
            raise
    
    # Get the images
    for offset in itertools.count(start, 20):
        print 'requesting posts starting from %d' % offset
        req = requests.get(REQUEST_URL % (blog, offset))
        req.raise_for_status()
        data = json.loads(req.text)
        if not data or not 'posts' in data or not data['posts']:
            print 'no posts returned'
            break
        for p, post in enumerate(data['posts']):
            if post['type'] == 'photo':
                print 'post #%d' % (offset + p)
                try:
                    # Save photoset posts
                    if 'photos' in post and post['photos']:
                        for ph, photo in enumerate(post['photos']):
                            download_photo(blog, post['id'], photo, ph)
                    # Save single-photo posts
                    else:
                        download_photo(blog, post['id'], post, 0)
                except requests.exceptions.HTTPError as exc:
                    print exc.message
                print 'saved images for post %s' % post['id']
        time.sleep(10)

if __name__ == '__main__':
    main()