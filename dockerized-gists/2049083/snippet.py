#!/usr/bin/env python
# coding: utf-8

import errno
import os
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
try:
    import requests
except ImportError:
    raise ImportError("Install requests with `pip install --user requests`")


# Adjust this:
INSTALL_PATH = "/home/pascal/Applications/chromium-daily"

GREEN_URL = "https://chromium-status.appspot.com/lkgr"
DOWNLOAD_URL = "http://commondatastorage.googleapis.com/chromium-browser-continuous/Linux_{arch}/{revision}/chrome-linux.zip"
REVISION_FILE = INSTALL_PATH + "/REVISION.txt"


def get_download_url(revision):
    machine = platform.machine()
    if machine == 'x86_64':
        arch = 'x64'
    else:
        # Obviously, this is a fairly risky assumption.
        arch = 'x86'

    return DOWNLOAD_URL.format(arch=arch, revision=revision)


def get_revision():
    request = requests.get(GREEN_URL)
    return request.text.strip()


def get_local_revision():
    try:
        return open(REVISION_FILE, 'r').read().strip()
    except IOError:
        return 0


def backup_old():
    # Remote previous
    old_path = INSTALL_PATH + "/chromium.old"
    shutil.rmtree(old_path, ignore_errors=True)
    try:
        os.rename(INSTALL_PATH + "/chrome-linux", old_path)
    except OSError:
        # Fails without prior install, obviously.
        pass


def unpack(file):
    zip = zipfile.ZipFile(file)
    zip.extractall(INSTALL_PATH)


def upgrade(revision):
    download_url = get_download_url(revision)
    dlfile = tempfile.NamedTemporaryFile()

    print("Starting download …")
    if subprocess.call(["wget", download_url, "-O", dlfile.name]) != 0:
        print("Download failed. New release probably hasn't been pushed yet.")
        sys.exit(1)

    print("Download finished.")

    backup_old()
    unpack(dlfile.name)

    # Make the chrome file executable.
    for executable in ('nacl_helper_bootstrap', 'nacl_helper', 'xdg-mime',
                       'xdg-settings', 'chrome', 'chrome-wrapper'):
        bin_path = os.path.join(INSTALL_PATH, "chrome-linux", executable)
        os.chmod(bin_path, 0o755)

    with open(REVISION_FILE, 'w') as revision_file:
        revision_file.write(unicode(revision))

    print("Done. Execute {} to start Chromium.".format(bin_path))


def main():
    try:
        os.makedirs(INSTALL_PATH)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    local_revision = get_local_revision()
    remote_revision = get_revision()
    print("Local: {}, Remote: {}".format(local_revision, remote_revision))

    if int(remote_revision) > int(local_revision):
        print("Upgrading …")
        upgrade(remote_revision)


if __name__ == "__main__":
    main()