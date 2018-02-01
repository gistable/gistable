# This file works with Python 2.7
# To make it work with Python 3 it need some modifications

# Example: python auto-commit.py -a="push" -c="My Commit" -b="master"
# If you left the commit variable empty or wrote `auto` it will generate
# a random commit from whatthecommit.com
# for more info run: python auto-commit.py -h

from os import system as execute
import argparse
import random, string
import urllib2
from HTMLParser import HTMLParser
import subprocess

# CONSTANTS
USERNAME = "YOUR_USERNAME"
PASSWORD = "YOUR_PASSWORD"


class AutoCommit:
    def __init__(self):
        pass

    def add_arguments(self, parser):
        parser.add_argument("-a", "--action", # argument names
                            nargs=1, # only one message allowed
                            type=str,
                            dest="action",
                            default=None, # default message for the commit
                            help="The git action to do, either pull or push")
        parser.add_argument("-c", "--commit", # argument names
                            nargs=1, # only one message allowed
                            type=str,
                            dest="commit",
                            default=None, # default message for the commit
                            help="Contain the message for the commit")
        parser.add_argument("-b", "--branch", # argument names
                            nargs=1, # only one message allowed
                            type=str,
                            dest="branch",
                            default="", # default message for the commit
                            help="The git branch you're working on")
        args = parser.parse_args()
        return args

    def set_arguments(self, args):
        options = {}
        for arg in vars(args):
            value = getattr(args, arg)
            if value:
                options[arg] = getattr(args, arg)[0].lower() # since we can only have one value!
            else:
                options[arg] = getattr(args, arg) # value is None
        self.options = options

    def execute_commad(self):
        try:
            actions = ["pull", "push"]
            if not self.options["action"]:
                raise ValueError('can not be empty', 'action')
            if self.options["action"] not in actions:
                raise ValueError('can only be `push` or `pull`', '--action/ -a')
            # if self.options["action"] == "push" and not self.options["branch"]:
            #     raise ValueError('please enter branch name to do the `push`', '--branch/ -b')

            if not self.options["commit"] or self.options["commit"] == "auto":
                random_string = ''.join(random.choice(string.lowercase) for i in range(10))
                request = urllib2.Request("http://www.whatthecommit.com/?r=" + random_string)
                response = urllib2.urlopen(request)
                html = response.read()

                html_parser = ResponseParser()
                html_parser.feed(html)
                html_parser.close()
                self.options["commit"] = html_parser.data[0].replace("\n", "")

            # repo = "https://%s:%s@github.com" % (USERNAME, PASSWORD)
            repo = "https://%s:%s@github.com/%s/Hellrazor.js.git/" % (USERNAME, PASSWORD, USERNAME)

            if self.options["action"] == "push":
                execute("git add .")
                execute("git commit -m '%s'" % (self.options["commit"], ))
                execute("git %s --repo %s" % (self.options["action"], repo))
            elif self.options["action"] == "pull":
                execute("git %s %s %s" % (self.options["action"], self.options["branch"], repo))
        except ValueError as e:
            print(e[1] + ": " + e[0])

class ResponseParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.recording = 0
        self.data = []
    def handle_starttag(self, tag, attrs):
        if tag != "p":
            return
        self.recording += 1

    def handle_endtag(self, tag):
        if tag != "p":
            return

    def handle_data(self, data):
        if self.recording != 1:
            return
        self.data.append(data)

if __name__ == '__main__':
    print("Auto git action will start...\n")

    parser = argparse.ArgumentParser(description="A lazy solution for doing git commits automatically")
    git = AutoCommit()
    args = git.add_arguments(parser)
    git.set_arguments(args)
    git.execute_commad()

    print("\nYour auto git action is done\n")
