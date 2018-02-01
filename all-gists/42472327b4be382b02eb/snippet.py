from pygit2 import Repository
from pygit2 import GIT_SORT_TOPOLOGICAL, GIT_SORT_REVERSE
import datetime
import json
import sys

class TzOffset(datetime.tzinfo):

    def __init__(self, offset=19800, name=None):
        self.offset = datetime.timedelta(seconds=offset)
        self.name = name or self.__class__.__name__

    def utcoffset(self, dt):
        return self.offset

    def tzname(self, dt):
        return self.name

    def dst(self, dt):
        return datetime.timedelta(0)

def fmtdate(obj):
  tz = TzOffset(offset=obj.offset*60, name=None)
  date = datetime.datetime.fromtimestamp(obj.time, tz)
  return date.strftime('%Y-%m-%d %H:%M:%S%z')

repo = Repository('.git')
commits = []
for commit in repo.walk(repo.head.target, GIT_SORT_TOPOLOGICAL):
  obj = {
    "commit": commit.hex,
    "abbreviated_commit": commit.hex[0:10],
    "tree": commit.tree.hex,
    "abbreviated_tree": commit.tree.hex[0:10],
    "parents": [x.hex for x in commit.parents],
    "abbreviated_parents": [x.hex[0:10] for x in commit.parents],
    "encoding": commit.message_encoding or '',
    "subject": commit.message.split('\n')[0],
    "body": commit.message,
    "author": {
      "name": commit.author.name,
      "email": commit.author.email,
      "date": fmtdate(commit.author)
      },
    "commiter": {
      "name": commit.committer.name,
      "email": commit.committer.email,
      "date": fmtdate(commit.committer)
      }
    }
  commits.append(obj)

json.dump(commits, sys.stdout, indent=4, sort_keys=True)
