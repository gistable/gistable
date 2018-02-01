import requests
import sys
import json
import re
import os
import string
import argparse

BASE_URL = 'https://api.twitch.tv'

def download_file(url, local_filename):
    print("downloading {0}".format(local_filename))
    CS = 1024
    done = 0
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=CS):
            if not chunk: # filter out keep-alive new chunks
                continue
            f.write(chunk)
            f.flush()
            done += CS
            sys.stdout.write("\r{0:>7.2f} MB".format(done/float(pow(1024,2))))


    print("done\n")

def download_broadcast(id_):
    """ download all video parts for broadcast 'id_' """

    pattern = '{base}/api/videos/a{id_}'
    url = pattern.format(base=BASE_URL, id_=id_)
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("API returned {0}".format(r.status_code))
    try:
        j = r.json()
    except ValueError as e:
        print("API did not return valid JSON: {}".format(e))
        print("{}".format(r.text))
        quit()

    qualities = j['chunks']
    res = [int(q[:-1]) for q in qualities if re.match("^\d+p", q)]
    best_resolution = "{}p".format(max(res))

    for nr, chunk in enumerate(j['chunks'][best_resolution]):
        video_url = chunk['url']
        ext = os.path.splitext(video_url)[1]
        filename = "{0}_{1:0>2}{2}".format(id_, nr, ext)
        download_file(video_url, filename)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('video_id', help='twitch video id')
    args = parser.parse_args()
    download_broadcast(args.video_id)
