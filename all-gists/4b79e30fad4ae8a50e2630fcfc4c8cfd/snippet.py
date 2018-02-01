import subprocess
import re
from dateutil import parser

class History(object):
    def __init__(self, commits):
        self._commits = ['%s' % n for n in commits if n.ot]

    def __iter__(self):
        return iter()

    def __str__(self):
        return '\n\n'.join(self._commits)

class Commit(object):
    _ot = False
    _quittingTime = 16

    def __init__(self, raw):
        self._pieces = [x.strip() for x in raw.split('\\n') if x != ''][:4]

        if (len(self._pieces) >=4):
            self._pieces = [re.sub(r'^([A-Z].*:\ )', '', x) for x in self._pieces]
            dateObj = parser.parse(self._pieces[2])
            self._pieces[2] = dateObj.strftime('%A %B %d %I:%M %p')

            if (dateObj.hour >= self._quittingTime or dateObj.weekday() >= 5):
                self._ot = True

    def __str__(self):
        return '\n'.join(self._pieces)

    @property
    def ot(self):
        return self._ot

def runSubProc(args):
    subp = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return str(subp.stdout.read())

def getHistory(user):
    logs = runSubProc(["git", "log", '--author=%s' % user, "--no-merges"])
    return History([Commit(x) for x in logs.split("commit")])

def main():
    user = runSubProc(["git", "config", "user.email"]).strip("b'")[:-2]
    logs = getHistory(user)
    print(logs)

if __name__ == '__main__':
    main()
