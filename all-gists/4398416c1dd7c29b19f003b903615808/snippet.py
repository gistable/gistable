#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import random as r
# https://pyzufall.readthedocs.io/
from pyzufall.generator import verbt, objekt

for i in range(1, 100):
    s = objekt()
    s = re.sub('der ', 'den ', s)
    if r.randint(0, 1):
        s = re.sub('den ', 'seinen ', s)
        s = re.sub('die ', 'seine ', s)
        s = re.sub('das ', 'sein ', s)
    print("Walulis " + verbt() + " " + s)
