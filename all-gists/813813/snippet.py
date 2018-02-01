#!/usr/bin/env python

import os
from munin import MuninPlugin

class TmpFileCount(MuninPlugin):
        title = "Number of Files in /tmp"
        args = "--base 1000 -l 0"
        vlabel = "files"
        scaled = False
        category = "system"

        @property
        def fields(self):
                warning = os.environ.get('files_warn', 10)
                critical = os.environ.get('files_crit', 120)
                return [("files", dict(
                        label = "files",
                        info = 'The number of files in /tmp',
                        type = "GAUGE",
                        min = "0",
                        warning = str(warning),
                        critical = str(critical)))]

        def execute(self):
                dircount = len(os.listdir("/tmp"))
                print "files.value %s" % dircount

if __name__ == "__main__":
        TmpFileCount().run()
