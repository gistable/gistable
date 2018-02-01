# based on https://launchpadlibrarian.net/94884626/testUtcToDst.patch
# from https://bugs.launchpad.net/dateutil/+bug/944123
import unittest
from datetime import datetime, timedelta

import dateutil.tz
import dateutil.zoneinfo
import pytz

tzname = "America/Toronto"
fmt = '%Y-%m-%d %H:%M:%S %Z%z'
before_utc_naive_dt = datetime(2011, 11, 6, 5, 30)
before_str = "2011-11-06 01:30:00 EDT-0400"
after_utc_naive_dt = before_utc_naive_dt + timedelta(hours=1)
after_str = "2011-11-06 01:30:00 EST-0500"


class TestPytzVsDateutil(unittest.TestCase):
    def _test(self, totz):
        self.assertEqual(totz(before_utc_naive_dt).strftime(fmt), before_str)
        self.assertEqual(totz(after_utc_naive_dt).strftime(fmt), after_str)

    def _test_dateutil(self, gettz):
        def totz(naive_utc_dt, utc=gettz("UTC"), tz=gettz("America/Toronto")):
            return naive_utc_dt.replace(tzinfo=utc).astimezone(tz)
        self._test(totz)

    def test_pytz(self):
        def totz(naive_utc_dt, utc=pytz.utc, tz=pytz.timezone(tzname)):
            return tz.normalize(
                naive_utc_dt.replace(tzinfo=utc).astimezone(tz))
        self._test(totz)

    def test_dateutil_tz(self):
        self._test_dateutil(dateutil.tz.gettz)

    def test_dateutil_zoneinfo(self):
        self._test_dateutil(dateutil.zoneinfo.gettz)


if __name__ == "__main__":
    unittest.main()