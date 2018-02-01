"""Twitter bot that tweets a random line from a file.

Uses Twisted to periodically select a random line from an input file,
and Twython to post it to Twitter using your credentials.

Usage: python twitterbot.py file.txt, where each line in file.txt is
a single sentence terminated by a newline ('\n').
"""

import sys
import random
import datetime
from twisted.internet import task
from twisted.internet import reactor
from twython import Twython

TIMEOUT = datetime.timedelta(hours=1).seconds
twitter = Twython("YOUR API KEY",
                  "YOUR API SECRET",
                  "YOUR ACCESS TOKEN",
                  "YOUR ACCESS TOKEN SECRET")


def reservoir(iterator):
    """Select item from iterator.

    Reservoir algorithm from http://stackoverflow.com/a/3540315/250241/
    """
    select = next(iterator)
    for num, item in enumerate(iterator):
        if random.randrange(num + 2):
            continue
        select = item
    return select


def get_line(file_name):
    """Open file and select tweetable line."""
    with open(file_name) as open_file:
        while True: # Loop until an appropriate sentence is found
            open_file.seek(0)  # reset file iterator to 0
            line = reservoir(open_file).strip().replace("  ", " ")
            if line[0].isupper() and 4 < len(line) < 140:
                return line


def tweet(sentence):
    """Tweet sentence to Twitter."""
    try:
        sys.stdout.write("{} {}\n".format(len(sentence), sentence))
        twitter.update_status(status=sentence)
    except:
        pass


def do_tweet(file_name):
    """Get line and tweet it"""
    line = get_line(file_name)
    tweet(line)


if __name__ == '__main__':
    file_name = str(sys.argv[1])
    l = task.LoopingCall(do_tweet, file_name)
    l.start(TIMEOUT)
    reactor.run()
