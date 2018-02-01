#!/usr/bin/env python3

#by luiz-rocha
#You can now download udemy lectures by this script which uses youtube-dl script :))

import getpass
import subprocess

try:
    url = input('Course URL: ')
    email = input('Udemy E-mail: ')
    pwd = getpass.getpass('Password: ')
    start = input('Playlist start: ')
    end = input('Playlist end: ')

    out_format = "%(playlist_index)s-%(title)s.%(ext)s"

    folder = "videos_downloads/"

    # If you use windows, try youtube-dl.exe
    command = "youtube-dl %s -o %s%s -u %s -p %s" % (
        url, folder, out_format, email, pwd
    )

    if start is not '':
        command += " --playlist-start " + start
    if end is not '':
        command += " --playlist-end " + end

    print("Starting Download ...")

    process = subprocess.call(command.split())

except KeyboardInterrupt:
    print("\nCtrl-C Detected")
except Exception as e:
    print("Something wrong occur:", e)
finally:
    print("Closed!")