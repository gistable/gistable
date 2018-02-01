#!/usr/bin/env python
#-------------------------------------------------
# file: twitcher.py
# author: Florian Ehmke
# description: dmenu for twitch streams
#-------------------------------------------------
import argparse
import requests
from subprocess import Popen, PIPE, STDOUT

class Stream(object):
    def __init__(self, name, status, viewers):
        self.name = name
        self.status = status
        self.viewers = viewers

    def display_string(self):
        display_string = "{} ({}) - {}\n".format(self.name,
                self.viewers, self.status).strip()
        return display_string + "\n"

def create_arg_parser():
    parser = argparse.ArgumentParser(description=
             'Open twitch stream through dmenu.')
    parser.add_argument(
        '-c', '--count', required=False, default=10, type=int,
        help='How many (default: 10) streams should be displayed?')
    parser.add_argument(
        '-g', '--game', required=False, default="Dota 2", type=str,
        help='Which game (default: Dota 2)?')
    parser.add_argument(
        '-q', '--quality', required=False, default="best", type=str,
        help='Which quality (default: best)?')
    return vars(parser.parse_args());

def main():
    args = create_arg_parser()

    count = args['count']
    game = args['game']
    quality = args['quality']

    dmenu_command = ['dmenu', '-l', str(count),
        '-nb', '#2D2D2D', '-nf', '#899CA1',
        '-sb', '#2D2D2D', '-sf', '#C0C0C0',
        '-fn', "-*-terminus-medium-*-*-*-16-*-*-*-*-*-*-*"]

    url = "https://api.twitch.tv/kraken/streams?limit=100&game=" \
          "{}&limit={}".format(game.replace(' ','+'), count)

    r = requests.get(url)
    json_streams = r.json()["streams"]
    streams = []
    for json_stream in json_streams:
        channel = json_stream["channel"]
        name = channel["name"]
        status = channel["status"]
        viewers = json_stream["viewers"]
        streams.append(Stream(name, status, viewers))

    dmenu_str = ""
    for stream in streams:
        dmenu_str += stream.display_string()
    dmenu_str.strip()

    p = Popen(dmenu_command, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    stream_selection = p.communicate(input=dmenu_str.encode('utf-8'))[0]
    if stream_selection:
        livestreamer_url = "twitch.tv/{} {}".format(stream_selection.
                            decode('utf-8').split()[0], quality)
        print(livestreamer_url)

if __name__ == "__main__":
    main()