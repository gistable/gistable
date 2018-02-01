import unittest
from mock import *
from datetime import datetime, timedelta
import time # so we can override time.time

mock_time = Mock()
mock_time.return_value = time.mktime(datetime(2011, 6, 21).timetuple())

class TestCrawlerChecksDates(unittest.TestCase):
    @patch('time.time', mock_time)
    def test_mock_datetime_now(self):
        self.assertEqual(datetime(2011, 6, 21), datetime.now())