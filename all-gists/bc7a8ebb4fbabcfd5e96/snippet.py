#!/usr/bin/env python3

import os
import subprocess

def stripValue(line):
    return line.split(':')[-1].strip()

class Apk:
    def __init__(self, apk):
        self.minSdkVersion = ''
        self.targetSdkVersion = ''
        self.sdkVersion = ''
        self.label = ''
        self.dump(apk)

    def dump(self, filename):
        cmd = 'aapt', 'd', 'badging', filename
        out = subprocess.Popen(cmd, stdout = subprocess.PIPE).stdout
        for line in out:
            try:
                linestr = line.decode('utf-8').strip()
            except:
                continue
            if linestr.startswith('application-label:'):
                self.label = stripValue(linestr)
            elif linestr.startswith('application-label-ko:'):
                self.label = stripValue(linestr)
            elif linestr.startswith('targetSdkVersion'):
                self.targetSdkVersion = stripValue(linestr)
            elif linestr.startswith('minSdkVersion'):
                self.minSdkVersion = lstripValue(linestr)
            elif linestr.startswith('sdkVersion'):
                self.sdkVersion = stripValue(linestr)
            else:
                pass
        if not self.targetSdkVersion:
            self.targetSdkVersion = self.sdkVersion
        if not self.minSdkVersion:
            self.minSdkVersion = self.sdkVersion

    def __str__(self):
        return """name: %s
min: %s target:%s
"""%(self.label, self.minSdkVersion, self.targetSdkVersion)

sout = open(1, 'w', encoding='utf-8', closefd=False)
for top, dirs, files in os.walk('.'):
    for filename in files:
        ext = os.path.splitext(filename)[-1]
        if not ext.endswith(".apk"):
            continue
        apk = os.path.join(top, filename)
        print(Apk(apk), file=sout)
