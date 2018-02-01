# -*- coding: utf-8 -*-

import os

if os.environ.get('READ_ENV', False):
  from honcho.command import Honcho
  h = Honcho()
  entries = h.read_env(type('obj', (object,), {'env': '.env', 'app_root': os.path.abspath(os.path.dirname(os.path.dirname(__file__)))})())
  h.set_env(entries)

DEBUG = os.environ.get('DEBUG', False)

# ...