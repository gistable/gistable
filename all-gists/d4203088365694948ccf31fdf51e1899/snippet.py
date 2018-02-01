#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Print cached git diff stats in less than 50 characters.

This script takes output from `git diff --cached --stat` and generates a single
line summary with less than 50 characters. This output may be used as a
(hopefully) temporary commit message like so

git commit -m "`blah.py`"

Please write good commit message!
'''

import subprocess
import os

raw = subprocess.check_output(['git', 'diff', '--cached', '--stat'])
if len(raw):
    lines = raw.split('\n')[:-1]
    summary = lines[-1][1:]
    if len(lines) == 2:
        summary_template = u"{} +{} -{}"
        summary_compontents = summary.split()

        plus = None
        minus = None
        if len(summary_compontents) >= 5:
            if '+' in summary_compontents[4]:
                plus = summary_compontents[3]
            else:
                minus = summary_compontents[3]
        if len(summary_compontents) >= 7:
            if '+' in summary_compontents[6]:
                plus = summary_compontents[5]
            else:
                minus = summary_compontents[5]
        if not plus:
            plus = '0'
        if not minus:
            minus = '0'
        file_path = lines[0].split('|')[0][1:-1]
        message = summary_template.format(file_path, plus, minus)
        if len(message) > 50:
            path, name = os.path.split(file_path)
            if path:
                file_path = os.path.join(u"…", name)
            else:
                file_path = name
            message = summary_template.format(file_path, plus, minus)
            if len(message) > 50:
                message = u"…" + message[-49:]
    else:
        message = summary

    print(message)
