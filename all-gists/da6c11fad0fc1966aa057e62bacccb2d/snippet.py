#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2016 Yannick Loiseau <me@yloiseau.net>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.
"""
on-modify hook for taskwarrior.

This hook connects taskwarrior and watson.

When starting a task in taskwarrior, the hook starts a corresponding project in
watson. The project and keywords of the taskwarrior task are used in watson.
When stopping a task in taskwarrior, the hook stops the watson project.

To install, copy in ~/.task/hooks/on-modify-watson.py and make it executable.

https://taskwarrior.org/
https://github.com/TailorDev/Watson
"""
import sys
import json
from watson import Watson


def load_json():
    return (json.loads(sys.stdin.readline()), json.loads(sys.stdin.readline()))


def is_starting(old, new):
    return "start" in new and "start" not in old


def is_stopping(old, new):
    return "start" in old and "start" not in new


def stop_watson():
    watson = Watson()
    if watson.is_started:
        watson.stop()
        watson.save()


def start_watson(task):
    watson = Watson()
    if watson.is_started and watson.config.getboolean('options', 'stop_on_start'):
        watson.stop()
    watson.start(task.get("project"), task.get("tags"))
    watson.save()


def main(args):
    try:
        old, new = load_json()
        print(json.dumps(new))
        if is_stopping(old, new):
            stop_watson()
            print("Watson project {} {} stopped".format(
                new.get("project"), new.get("tags")))
        elif is_starting(old, new):
            start_watson(new)
            print("Watson project {} {} started".format(
                new.get("project"), new.get("tags")))
        return 0
    except Exception as e:
        print(str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
