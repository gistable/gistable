#!/usr/bin/env python
import httplib, urllib
import subprocess
import time
import socket

# Configuration #########################################################

BACKUP_PREFIX=socket.gethostname() + "_"
MAX_BACKUPS=30
BACKUP_ITEMS=[
        "/etc",
        "/root"
]

PUSHOVER_TOKEN="TOKEN HERE"
PUSHOVER_USER="USER HERE"
NOTIFY_ON_SUCCESS=True

################k#########################################################

def notify(title, message, priority):
        conn = httplib.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
          urllib.urlencode({
            "token": PUSHOVER_TOKEN,
            "user": PUSHOVER_USER,
            "message": message,
            "title":title,
            "priority": priority
          }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()

# Perform Backup #########################################################

try:
        result = subprocess.check_output([
                "tarsnap",
                "-c",
                "--quiet",
                "-f", BACKUP_PREFIX + time.strftime('%Y%m%d%H%M%S'),
                ] + BACKUP_ITEMS, stderr=subprocess.STDOUT)
        if NOTIFY_ON_SUCCESS:
                notify("Backup Complete", result, -1)
except subprocess.CalledProcessError as e:
        notify("Backup FAILED", "Error {0} - {1}".format(e.returncode, e.output), 1)


# Perform Pruning ########################################################

archives = subprocess.check_output(["tarsnap","--list-archives"]).split()
archives = [s for s in archives if s.startswith(BACKUP_PREFIX)]
archives.sort()
archives.reverse()
archives_to_prune = archives[MAX_BACKUPS:]
for archive in archives[MAX_BACKUPS:]:
        try:
                result = subprocess.check_output([
                        "tarsnap",
                        "-d",
                        "--quiet",
                        "-f", archive
                        ], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
                notify("Pruning FAILED", "Error {0} - {1}".format(e.returncode, e.output), 1)
