#!/usr/bin/env python

import git
import json
import sqlite3
import re
import os
import os.path

def log(repo):
    repo = git.Repo(repo)
    log = repo.git.log().split("\ncommit ")
    commits = []
    for line in log:
        match = re.search(r"([^\n]+)\nAuthor:\s+([^\n]+)\nDate:\s+([^\n]+)\n\n\s+(.*)\n", line, re.DOTALL)
        if match:
            author = re.match(r"(.+)\s+<([^>]+)>", match.group(2))
            commit = {
                "hash": match.group(1),
                "date": match.group(3),
                "message": match.group(4)
            }
            if author:
                commit["author"] = author.group(1)
                commit["email"] = author.group(2)
            else:
                commit["author"] = match.group(2)
                commit["email"] = None
            commits.append(commit)
    return commits



if __name__ == '__main__':
    path = os.getcwd()
    commits = log(path)
    if not path.endswith("/"):
        path = path + "/"
    fname = "%sgit.sqlite" % (path)
    if os.path.isfile(fname):
        os.remove(fname)
    con = sqlite3.connect(fname)
    con.execute("CREATE TABLE commits (hash VARCHAR(40), author VARCHAR(256), email VARCHAR(256), " +
                "message text, date VARCHAR(35))")
    cur = con.cursor()
    def commit(c):
        return (c["hash"], c["author"], c["email"], c["message"], c["date"])
    cur.executemany("INSERT INTO commits VALUES(?, ?, ?, ?, ?)", map(commit, commits))
    con.commit()
    con.close()
