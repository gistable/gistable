#!/usr/bin/python3
# Use: ./8ch-downloader.py <thread url>
import requests, os, json, sys

def download(url, name, subject_path):
    filepath = subject_path + '/' + name
    if not os.path.exists(filepath):
        print('Get got: ' + name)
        r = requests.get(url, stream=True)
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
    return True


def get_images(thread_url):
    thread_json_url = thread_url.replace('html', 'json')
    board = thread_url.split('/')[3] # is this really safe?
    posts = json.loads(requests.get(thread_json_url).text)['posts'] # nesting at its best
    # no directory? no problem!
    subject_path = './' + posts[0].get('sub', str(posts[0].get('no'))) # use thread number if there's no subject
    if not os.path.exists(subject_path):
            os.makedirs(subject_path)

    def gk(key, value): # lazy shortcut, don't know if it's actually a good idea
        return value.get(key, '')

    for post in posts:
        if gk('filename', post):
            or_filename = gk('filename', post)
            filename = gk('tim', post) + gk('ext', post)
            download('http://8ch.net/' + board + '/src/' + filename, or_filename + gk('ext', post), subject_path)
        if gk('extra_files', post): # they gotta be covered
            for extra_file in gk('extra_files', post):
                orf = gk('filename', extra_file)
                fin = gk('tim', extra_file) + gk('ext', extra_file)
                download('http://8ch.net/' + board + '/src/' + fin, orf + gk('ext', extra_file), subject_path)

get_images(sys.argv[1:][0])