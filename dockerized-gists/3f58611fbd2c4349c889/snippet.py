# ~/.ipython/profile_default/startup/00_common.py
import base64
import codecs
import cPickle as pickle
import cStringIO as StringIO
import csv
import hashlib
import importlib
import json
import math
import os
import random
import re
import shutil
import struct
import sys
import tempfile
import urllib
import urlparse
import uuid

from contextlib import contextmanager
from datetime import date, datetime, timedelta
from decimal import Decimal
