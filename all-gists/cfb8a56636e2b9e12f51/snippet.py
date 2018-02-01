#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64

MESSAGE = '''
EUYQGhMMSx0cU0FIU1MCFAQPG01NQ0gTAEICChUGBxZTRVxBSQoZFQYKHQpKSUNURhcVEgoUFR1I
SltDSBkBTRwKEAgQHxFCSkFJDgkJCgoGCkMLAQBGUklUQhMPAgAJCgYLV0MOSR0VAxAaABZBQVRP
TRICCRVIAk5IEg4dVFRfRkYZBgRARBI=
'''

KEY = 'jacopo.notarstefano'

result = []
for i, c in enumerate(base64.b64decode(MESSAGE)):
    result.append(chr(ord(c) ^ ord(KEY[i % len(KEY)])))

print ''.join(result)