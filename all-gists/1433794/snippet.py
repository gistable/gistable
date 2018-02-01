#!/usr/bin/python
#
# git-slim
#
# Remove big files from git repo history.
#
# Requires GitPython (https://github.com/gitpython-developers/GitPython)
#
# References:
# - http://help.github.com/remove-sensitive-data/
# - http://stackoverflow.com/questions/4444091/git-filter-branch-to-delete-large-file
# - http://stackoverflow.com/questions/1029969/why-is-my-git-repository-so-big/1036595#1036595
# - http://stackoverflow.com/questions/460331/git-finding-a-filename-from-a-sha1

from glob import glob
from git import Repo
from os.path import getsize
from re import split
from shutil import rmtree
from sys import argv, exit, stdout


def print_activity(start, end='done'):
    '''Decorator which logs info like "Doing something: done" to stdout.'''
    def decorate(f):
        def wrapped(*args, **kwargs):
            stdout.write('%s: ' % start)
            stdout.flush()
            x = f(*args, **kwargs)
            print end
            return x
        return wrapped
    return decorate


def slim_main():
    '''Invoke slimming on working directory or first argv entry.'''
    repo_dir = argv[1] if len(argv) > 1 else '.'
    try:
        slim(repo_dir)
    except KeyboardInterrupt:
        exit(0)


def slim(repo_dir):
    r = Repo(repo_dir)
    prep(r)
    old_size = repo_size(r)
    slim_blobs(r)
    tidy_up(r)
    new_size = repo_size(r)
    ok_done(old_size, new_size)


def repo_size(r):
    return getsize(r.git_dir)


def prep(r):
    '''Prep a repo by running GC and repacking.'''
    if r.is_dirty():
        raise Exception('repo is dirty')
    gc(r)
    repack(r)


def slim_blobs(r):
    '''Reduce repo size by listing blobs in size order and asking the user if
    they would like to remove them.

    '''
    pack_blobs = list_pack_blobs_by_size(r)
    index = blob_index(r)
    seen = []
    targets = []
    for b in pack_blobs:
        if b[0] not in index:
            print '%s not in blob index' % b[0]
        else:
            blob_path, commit_hexsha = index[b[0]]
            if blob_path not in seen:
                blob_size = format_size(b[1])
                commit_hexsha_prefix = commit_hexsha[:7]
                prompt = 'Remove %s (%s at %s)? [Y/n/d] ' % \
                        (blob_path, blob_size, commit_hexsha_prefix)
                answer = raw_input(prompt).strip().lower()
                if answer == 'd':
                    break
                elif answer in ('y', ''):
                    targets.append(blob_path)
                seen.append(blob_path)
    remove_files(r, targets)


def blob_index(r):
    '''Build index of paths of blobs in the repo. Iterates across all files in
    all commits and records blob used.

    '''
    desc = 'Indexing blobs in commits: '
    index = {}
    commits = list(r.iter_commits())
    commits_len = len(commits)
    blob_predicate = lambda i, d: i.type == 'blob'
    i = 1
    for commit in commits:
        stdout.write('\r%s(%s/%s)' % (desc, i, commits_len))
        stdout.flush()
        for blob in commit.tree.traverse(predicate=blob_predicate):
            index[blob.hexsha] = blob.path, str(commit)
        i += 1
    print '\r%sdone                                        ' % desc
    return index


@print_activity('Listing pack blobs')
def list_pack_blobs_by_size(r):
    blobs = list_pack_blobs(r)
    blobs_s = sorted(blobs, key=lambda b: b[1], reverse=True)
    return blobs_s


def list_pack_blobs(r):
    '''Call git verify-pack to dump info about blobs in a pack.'''
    pack_index_glob = r.git_dir + '/objects/pack/pack-*.idx'
    pack_index_files = glob(pack_index_glob)
    pack_info = r.git.verify_pack(*pack_index_files, verbose=True)
    return extract_blob_info(pack_info)


def extract_blob_info(pack_info):
    '''Extract info about blobs in a pack from text returned by git verify-pack.

    '''
    for line in pack_info.split('\n'):
        bits = split(r'\s+', line)
        if len(bits) > 1 and bits[1] == 'blob':
            yield bits[0], int(bits[3])


def format_size(num):
    '''Format numbers as file sizes. From hurry.filesize.'''
    for x in [' bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%.0f%s" % (num, x)
        num /= 1024.0


@print_activity('Removing files from repo history')
def remove_files(r, fs):
    '''Run git rm for each file in list against each commit using git
    filter-branch. Completely removes files from repo history.

    '''
    if not fs:
        return
    # todo: check file list doesn't exceed max command length
    filelist = ' '.join(fs)
    r.git.filter_branch('--index-filter',
            'git rm --cached --ignore-unmatch %s' % filelist,
            '--prune-empty',
            'HEAD')


def tidy_up(r):
    '''Tidy up by expiring reflog, aggresively GCing repo and repacking. Should
    recover space used by objects removed during slimming process.

    '''
    rm_original_refs(r)
    expire_reflog(r)
    gc(r)
    repack(r)


@print_activity('Removing original refs')
def rm_original_refs(r):
    rmtree(r.git_dir + '/refs/original/', ignore_errors=True)


@print_activity('Expiring reflog')
def expire_reflog(r):
    r.git.reflog('expire', '--expire=now', '--all')


@print_activity('Garbage collecting')
def gc(r):
    r.git.gc(prune=True)


@print_activity('Repacking')
def repack(r):
    r.git.repack(a=True, d=True, q=True)


def ok_done(old_size, new_size):
    delta = format_size(old_size - new_size)
    old_f = format_size(old_size)
    new_f = format_size(new_size)
    print '\nRepo slimmed by %s (reduced from %s to %s)' % (delta, old_f, new_f)
    print '(Running \'git gc --agressive --prune\' may reclaim further space)\n'
    print 'Next run \'git push origin --all --force\''
    print 'Then re-clone all copies of the repo'
    print 'Warning: If an old clone is used, big objects may reappear'


if __name__ == '__main__':
    slim_main()