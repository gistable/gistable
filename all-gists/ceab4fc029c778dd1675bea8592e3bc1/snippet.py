#!/usr/bin/python
"""
Karl's unix/rsync time-machine script.
Maintains daily and monthly snapshots of a directory tree, hard linked to save
space when files don't change.
Inspired by http://www.mikerubel.org/computers/rsync_snapshots/, but using
more robust coding practices.

Features:

* The script fails if it's currently already running
* Each snapshot is created as a temp dir and then renamed only upon success
* Daily and monthly parameters can be easily changed
* Errors will not pass silently
* The entire script is crash safe; just re-run it to retry an error

Configuration:

This script runs SNAP_RSYNC_CMD to incrementally mirror a directory (e.g.
your home directory) to SNAP_DEST_DIR.  Ideally, SNAP_DEST_DIR is on a
different drive for durability.  Then daily and monthly snapshots are created
in SNAP_DEST_DIR.  The maximum we keep are SNAP_MAX_DAILY and
SNAP_MAX_MONTHLY, respectively; all others are automatically deleted.

Usage:

1) Configure the variables below
2) Run this script without any args (preferably daily via cron as your user id)
"""
import fcntl
import os
import shutil
import subprocess
import sys
import time


SNAP_DEST_DIR = "/mnt/raid3tb/karlsnap"
SNAP_DAILY_PREFIX = "snapshot_day_"
SNAP_MONTHLY_PREFIX = "snapshot_month_"
SNAP_MAX_DAILY = 7
SNAP_MAX_MONTHLY = 12
SNAP_TMP = os.path.join(SNAP_DEST_DIR, "snapshot_tmp")
SNAP_MIRROR = os.path.join(SNAP_DEST_DIR, "mirror")
SNAP_RSYNC_CMD = [
        "rsync", 
        "-rlptgo",   # Recursive, symlinks, perms, times, group, owner
        "-v",        # Verbose
        "--delete",
        "--delete-excluded",
        "--exclude", ".thumbnails",
        "--exclude", ".cache",
        "--exclude", ".gvfs",
        "/home/karl/",  # Trailing slash *required* to select contents
        SNAP_MIRROR]  


def _get_snapshots(prefix):
    """
    Return list of snapshot dir paths, 
    sorted as newest first, oldest last.
    @prefix: filter only snapshot dirs that start with this string
    """
    ret = []
    for name in os.listdir(SNAP_DEST_DIR):
        if name.startswith(prefix):
            path = os.path.join(SNAP_DEST_DIR, name)
            ret.append(path)
    ret.sort(reverse=True)
    return ret


def _print(msg):
    """
    Write to stdout and flush it, so our output isn't mixed with subprocesses
    """
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


def _delete_old_snapshots(prefix, nr_keep):
    """
    Delete all but @nr_keep newest snapshots,
    with their prefix matching @prefix
    """
    snapshots = _get_snapshots(prefix)
    snapshots_keep = snapshots[0:nr_keep]
    snapshots_delete = snapshots[nr_keep:]
    for snap in snapshots_keep:
        _print("keeping snapshot      %s" % snap)
    for snap in snapshots_delete:
        _print("deleting old snapshot %s" % snap)
        _delete_directory(snap)


def _delete_directory(path):
    """
    Blow away a directory.
    Don't fail if there are read-only subdirectories.
    (Read-only files aren't a problem for rmtree)
    """
    # Fix potential permission problems.  
    DIR_PERMS = 0755
    for (a,b,c) in os.walk(path):
        os.chmod(a, DIR_PERMS)
    shutil.rmtree(path)
        

"""
The snapshot dir names are ascii-sortable.
Year, month, and day are fixed length fields.
This is crash-safe and easier than trying to 
shuffle .1, .2, .3 dirs on every rotation.
"""
def _get_daily_snapshot_name():
    #dt = time.strftime("%Y-%m-%d-%H%M%S", time.localtime())
    dt = time.strftime("%Y-%m-%d", time.localtime())
    name = SNAP_DAILY_PREFIX + dt
    return os.path.join(SNAP_DEST_DIR, name)


def _get_monthly_snapshot_name():
    dt = time.strftime("%Y-%m", time.localtime())
    name = SNAP_MONTHLY_PREFIX + dt
    return os.path.join(SNAP_DEST_DIR, name)


def _update_mirror():
    """
    Create or update the SNAP_MIRROR dir using rsync
    """
    _print("Updating base archive: %s" % SNAP_MIRROR)
    args = SNAP_RSYNC_CMD
    _print("Running %s" % args)
    p = subprocess.Popen(args)
    rc = p.wait()
    if rc != 0:
        raise Exception("rsync failed")


def _create_snapshot(snap):
    """
    cp -al SNAP_MIRROR to a new snapshot 
    snap: full path name of snapshot
    Do nothing if @snap already exists
    Use a tmp dir (SNAP_TMP) and rename it when successful, for failure safety
    """
    # Clean up any previous failure
    if os.path.exists(SNAP_TMP):
        _delete_directory(SNAP_TMP)

    if os.path.exists(snap):
        _print("snapshot %s already exists" % snap)
        return

    _print("Linking new snapshot: %s" % snap)
    args = ["cp", "-al", SNAP_MIRROR, SNAP_TMP]
    p = subprocess.Popen(args)
    rc = p.wait()
    if rc != 0:
        raise Exception("cp failed")

    # Success: atomically rename it to an official snapshot
    os.rename(SNAP_TMP, snap)


def _lock_file_exclusively(path):
    """
    Open @path and lock it exlusively.
    Return: file object, which you must maintain a reference to 
    (if it is closed, the lock is released).
    Raises: IOError on failure
    """
    _print("Locking file %s" % path)
    lock_file = open(path)
    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    return lock_file


def main():
    # Ensure this script is not running concurrently.
    # This is a safety feature if cron is calling it too quickly.
    lock_file = _lock_file_exclusively(sys.argv[0])

    _update_mirror()
    _create_snapshot(_get_daily_snapshot_name())
    _create_snapshot(_get_monthly_snapshot_name())
    _delete_old_snapshots(SNAP_DAILY_PREFIX, SNAP_MAX_DAILY)
    _delete_old_snapshots(SNAP_MONTHLY_PREFIX, SNAP_MAX_MONTHLY)


if __name__ == "__main__":
    main()
