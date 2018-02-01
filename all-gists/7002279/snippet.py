#!/usr/bin/python
#coding: utf-8
'''

requirements: 
    GitPython
    MySQLdb
    TofApi.py
'''

from git import *
import time
import MySQLdb as mdb
from TofApi import TofApi

GIT_PATH = '/path/to/yyy.git'
URL_TEMPLATE = 'http://xxx/yyy/commit/%s (%s)'
NOW = time.time()
# 604800 = 7 * 24 * 60 * 60
TO_TIME_POINT = NOW - 604800

commit_tracked = []
commits_by_author = {}


def pack_git_commit():
    repo = Repo(GIT_PATH)
    commit = repo.heads.master.commit

    def track_commit(commit_ref):
        commit_time = commit_ref.committed_date
        if commit_ref not in commit_tracked and commit_time >= TO_TIME_POINT:
            commit_tracked.append(commit_ref)
            commit_author = commit_ref.author.email
            commit_message = (commit_ref.message).strip('\n')
            if commits_by_author.has_key(commit_author):
                commits_by_author[commit_author].append((commit_ref.hexsha, commit_time, commit_message))
            else:
                commits_by_author[commit_author] = [(commit_ref.hexsha, commit_time, commit_message)]
            if len(commit_ref.parents) > 0:
                for parent_commit in commit_ref.parents:
                    track_commit(parent_commit)

    track_commit(commit)


def sort_by_commit_time():
    for key, value in commits_by_author.iteritems():
        commits_by_author[key] = sorted(value, key=lambda item: item[1])


def email_commits():
    api = TofApi()
    sender = 'xxx@xxx.com'

    def shuffle_authors():
        import random

        authors = commits_by_author.keys()
        random.shuffle(authors)
        return authors
    emails = shuffle_authors()
    emails.append(emails[0])
    emails_count = len(emails)
    for index in xrange(emails_count - 1):
        receiver = emails[index]
        title = '请评审%s本周提交的代码' % emails[index+1]
        task_list = []
        for commit in commits_by_author[emails[index+1]]:
            task_list.append(URL_TEMPLATE % (commit[0], commit[2]))
        content = '本周你的代码评审任务为：\n%s\n请尽快处理，谢谢！' % ('\n'.join(task_list)).encode('utf-8')
        print sender, receiver, title, content
        api.send_mail(sender, receiver, title, content)


def main():
    pack_git_commit()
    sort_by_commit_time()
    email_commits()


if __name__ == '__main__':
    main()