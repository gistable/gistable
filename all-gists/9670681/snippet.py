#!/usr/bin/env python
# encoding: utf-8
"""
utc_to_local.py

Example of converting UTC to local time using python-dateutil.

https://pypi.python.org/pypi/python-dateutil
"""
from datetime import datetime
from dateutil.tz import tzutc, tzlocal

utc = datetime.now(tzutc())
print('UTC:   ' + str(utc))

local = utc.astimezone(tzlocal())
print('Local: ' + str(local))