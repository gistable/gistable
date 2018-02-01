#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from mock import patch

from django.test import TestCase
from django.utils import timezone


class DatesTestCase(TestCase):

    def test_date(self):
        with patch.object(timezone, 'now', return_value=datetime.datetime(2015, 1, 8, 11, 00)) as mock_now:
            # some code
