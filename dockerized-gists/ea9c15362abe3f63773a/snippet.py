#!/usr/bin/env python
from __future__ import print_function

import sys
import os
import glob
import shutil
import sqlite3
from os.path import join as joinpath, expanduser, exists, isabs


QUERY_ATTACHMENTS="""
    SELECT (REPLACE(itemAttachments.path, 'storage:', items.key || '/')) 
    FROM itemAttachments 
    LEFT JOIN items ON itemAttachments.itemID=items.itemID
    """

class Zotero(object):
    def __init__(self, mode="r"):
        self.sql = None
        self.root = self._find_root()
        self.database = joinpath(self.root, "zotero", "zotero.sqlite")
        self.storage = joinpath(self.root, "zotero", "storage")

        if not exists(self.database):
            raise RuntimeError("missing zotero database %r"%self.database)

        self.sql = self._open_database(mode)
        self.cursor = self.sql.cursor()

    def close(self):
        self.sql.close()
        self.sql = None

    def __del__(self):
        if self.sql is not None:
            self.close()

    def _find_root(self):
        env_root = os.environ.get("ZOTERO_HOME", None)
        if env_root is not None:
            return env_root
        if sys.platform == 'darwin':
            app_support = expanduser("~/Library/Application Support/")
            profiles = glob.glob(joinpath(app_support, "Firefox", "Profiles", "*"))
            profiles += glob.glob(joinpath(app_support, "Zotero", "Profiles", "*"))
            if len(profiles) > 1: 
                raise ValueError("Set ZOTERO_HOME to determine zotero profile:\n    "
                    +"\n    ".join(profiles))
            return profiles[0]
        else:
            raise RuntimeError("Only mac support.  See https://www.zotero.org/support/zotero_data for other OSes")
        
    def _open_database(self, mode):
        if mode == "r":
            # Copy the zotero database to tmp so that we don't interfere with
            # running versions.
            # TODO: use mkstemp or similar
            dbcopy = "/tmp/zotero.sqlite"
            shutil.copy(self.database, dbcopy)
            return sqlite3.connect(dbcopy)
        else:
            return sqlite3.connect(self.database)

    def attachments(self):
        linked = []
        stored = []
        missing = []
        empty = []
        for rows in self.cursor.execute(QUERY_ATTACHMENTS):
            # TODO: identify item by Title and Creator
            # TODO: identify collection(s) containing item
            path = rows[0]
            if not path:
                continue
            path = path.encode('latin1')
            if not isabs(path):
                stored.append(path)
                full_path = joinpath(self.storage, path)
            else:
                linked.append(path)
                full_path = path
            if not exists(full_path):
                missing.append(path)
        missing = set(missing)
        linked = set(linked) - set(missing)
        stored = set(stored) - set(missing)
        empty = set(empty)
        return linked, stored, missing, empty

def main():
    zot = Zotero()
    linked, stored, missing, empty = zot.attachments()
    zot.close()

    if stored and linked:
        print("Files stored in %r:\n   "%zot.storage,
              "\n    ".join(sorted(stored)))
    if missing:
        print("Missing files:\n   ",
              "\n    ".join(sorted(missing)))


if __name__ == "__main__":
    main()
