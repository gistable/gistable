import argparse
import os
import re
import threading
import urllib
import requests
import sys

urls = []
global stop
stop = 0
event = threading.Event()
event.clear()


def main():
    lock = threading.Lock()
    parser = argparse.ArgumentParser(description="Download images from 4chan")
    parser.add_argument('url')
    parser.add_argument('-t', '--threads')
    parser.add_argument('-f', '--filename')
    args = parser.parse_args()

    default_threads = 4
    if args.threads:
        default_threads = args.threads

    filename = "%id_thread%/%filename%%ext%"
    if args.filename:
        filename = args.filename

    regex = re.search("https?://boards.4chan.org/([a-z0-9]{1,4})/res/(\d+)", args.url)
    if not regex:
        print "url not valid"
        exit()
    board = regex.group(1)
    id_thread = regex.group(2)
    json_url = "https://a.4cdn.org/" + board + "/res/" + id_thread + ".json"

    try:
        r = requests.get(json_url)
    except requests.ConnectionError:
        print "Connection Error"
        exit()

    if r.status_code != 200:
        print "error opening 4chan"
        exit()

    json = r.json()
    for post in json["posts"]:
        try:
            if post["filename"]:
                img_url = "http://i.4cdn.org/" + board + "/src/" + str(post["tim"]) + post["ext"]
                name = {}
                for i in post:
                    name[i] = post[i]
                name["board"] = board
                name["id_thread"] = id_thread
                urls.append([img_url, name])
        except KeyError:
            pass

    path = get_fullname(urls[0], filename)
    directory = os.path.dirname(os.path.expanduser(path))
    if not os.path.exists(directory):
        os.makedirs(directory)

    for ai in range(0, int(default_threads)):
        t = DownloadImage(lock, default_threads, filename, directory)
        t.start()

    try:
        while not event.is_set():
            pass
    except KeyboardInterrupt:
        global stop
        stop = 1
        print "Interrupted"
        sys.exit(0)

    print "Finished!"
    sys.exit(1)


def get_fullname(url, filename):
    path = ""
    for i in filename.split("%"):
        try:
            path += str(url[1][i])
        except KeyError:
            path += str(i)
    return path


def get_filename(url, filename, directory):
    path = directory + "/"
    for i in os.path.basename(filename).split("%"):
        try:
            path += str(url[1][i])
        except KeyError:
            path += str(i)
    return path


class DownloadImage(threading.Thread):
    def __init__(self, lock, threads, filename, directory):
        threading.Thread.__init__(self)
        self.lock = lock
        self.threads = threads
        self.filename = filename
        self.directory = directory

    def run(self):
        global stop
        while urls:
            if stop == 1:
                exit()
            self.lock.acquire()
            try:
                url = urls.pop()
                print url[0] + " --> " + get_filename(url, self.filename, self.directory) + " (" + self.name + ")"
            except IndexError:
                print 'Url finished!'
                self.lock.release()
                exit()
            self.lock.release()
            if not os.path.exists(get_filename(url, self.filename, self.directory)):
                urllib.urlretrieve(url[0], get_filename(url, self.filename, self.directory))
        event.set()
        exit()


if __name__ == '__main__':
    main()