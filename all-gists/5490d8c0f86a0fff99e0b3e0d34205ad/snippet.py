from __future__ import print_function

import sys
from datetime import datetime
from time import time

try:
    import arrow
except ImportError:
    print('pip install arrow')
    sys.exit(1)

try:
    import delorean
except ImportError:
    print('pip install Delorean')
    sys.exit(1)

try:
    import pendulum
except ImportError:
    print('pip install pendulum')
    sys.exit(1)

try:
    import udatetime
except ImportError:
    print('pip install udatetime')
    sys.exit(1)

import pytz


def get_local_utc_offset():
    ts = time()
    return (
        datetime.fromtimestamp(ts) - datetime.utcfromtimestamp(ts)
    ).total_seconds() / 60


RFC3339_DATE = '2016-07-18'
RFC3339_TIME = '12:58:26.485897-02:00'
RFC3339_DATE_TIME = RFC3339_DATE + 'T' + RFC3339_TIME

DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
DATETIME_OBJ = datetime.strptime(RFC3339_DATE_TIME[:-6], DATE_TIME_FORMAT)\
    .replace(tzinfo=pytz.FixedOffset(get_local_utc_offset() * -1))
TIME = time()


def benchmark_parse():
    def _datetime():
        dt = datetime.strptime(RFC3339_DATE_TIME[:-6], DATE_TIME_FORMAT)

        if RFC3339_DATE_TIME[-6] in ('+', '-'):
            negative = False

            if RFC3339_DATE_TIME[-6] == '-':
                negative = True

            (hour, minute) = RFC3339_DATE_TIME[-5:].split(':')
            hour = int(hour)
            minute = int(minute)
            offset = (hour * 60) + minute

            if negative:
                offset = offset * -1

            return dt.replace(tzinfo=pytz.FixedOffset(offset))

        return dt.replace(tzinfo=pytz.FixedOffset(0))

    def _udatetime():
        return udatetime.from_string(RFC3339_DATE_TIME)

    def _arrow():
        return arrow.get(RFC3339_DATE_TIME)

    def _pendulum():
        return pendulum.parse(RFC3339_DATE_TIME)

    def _delorean():
        return delorean.parse(RFC3339_DATE_TIME)

    return (_datetime, _udatetime, _arrow, _pendulum, _delorean)


def benchmark_format():
    def _datetime():
        offset = DATETIME_OBJ.tzinfo.utcoffset(None).total_seconds() / 60
        tz = ''

        if offset < 0:
            offset = offset * -1
            tz = '-%02d:%02d' % (offset / 60, offset % 60)
        else:
            tz = '+%02d:%02d' % (offset / 60, offset % 60)

        return DATETIME_OBJ.strftime(DATE_TIME_FORMAT) + tz

    uda = udatetime.from_string(RFC3339_DATE_TIME)

    def _udatetime():
        return udatetime.to_string(uda)

    arr = arrow.get(RFC3339_DATE_TIME)

    def _arrow():
        return arr.isoformat()

    pen = pendulum.parse(RFC3339_DATE_TIME)

    def _pendulum():
        return pen.to_rfc3339_string(True)

    delo = delorean.parse(RFC3339_DATE_TIME)

    def _delorean():
        offset = delo.datetime.tzinfo.utcoffset(None).total_seconds() / 60
        tz = ''

        if offset < 0:
            offset = offset * -1
            tz = '-%02d:%02d' % (offset / 60, offset % 60)
        else:
            tz = '+%02d:%02d' % (offset / 60, offset % 60)

        return delo.datetime.strftime(DATE_TIME_FORMAT) + tz

    return (_datetime, _udatetime, _arrow, _pendulum, _delorean)


def benchmark_utcnow():
    def _datetime():
        return datetime.utcnow().replace(tzinfo=pytz.FixedOffset(0))

    def _udatetime():
        return udatetime.utcnow()

    def _arrow():
        return arrow.utcnow()

    def _pendulum():
        return pendulum.utcnow()

    def _delorean():
        return delorean.utcnow()

    return (_datetime, _udatetime, _arrow, _pendulum, _delorean)


def benchmark_now():
    def _datetime():
        return datetime.now().replace(
            tzinfo=pytz.FixedOffset(get_local_utc_offset())
        )

    def _udatetime():
        return udatetime.now()

    def _arrow():
        return arrow.now()

    def _pendulum():
        return pendulum.now()

    def _delorean():
        return delorean.now()

    return (_datetime, _udatetime, _arrow, _pendulum, _delorean)


def benchmark_fromtimestamp():
    def _datetime():
        return datetime.fromtimestamp(TIME).replace(
            tzinfo=pytz.FixedOffset(get_local_utc_offset())
        )

    def _udatetime():
        return udatetime.fromtimestamp(TIME)

    def _arrow():
        return arrow.Arrow.fromtimestamp(TIME)

    def _pendulum():
        return pendulum.fromtimestamp(TIME)

    def _delorean():
        dt = datetime.fromtimestamp(TIME)
        return delorean.Delorean(
            datetime=dt, timezone=pytz.FixedOffset(get_local_utc_offset())
        )

    return (_datetime, _udatetime, _arrow, _pendulum, _delorean)


def benchmark_utcfromtimestamp():

    def _datetime():
        return datetime.utcfromtimestamp(TIME)\
            .replace(tzinfo=pytz.FixedOffset(0))

    def _udatetime():
        return udatetime.utcfromtimestamp(TIME)

    def _arrow():
        return arrow.Arrow.utcfromtimestamp(TIME)

    def _pendulum():
        return pendulum.utcfromtimestamp(TIME)

    def _delorean():
        return delorean.epoch(TIME)

    return (_datetime, _udatetime, _arrow, _pendulum, _delorean)

if __name__ == '__main__':
    import timeit

    benchmarks = [
        benchmark_parse,
        benchmark_format,

        benchmark_utcnow,
        benchmark_now,

        benchmark_fromtimestamp,
        benchmark_utcfromtimestamp,
    ]
    test_only = False

    if len(sys.argv) == 2 and sys.argv[1] == 'test':
        test_only = True

    print('Executing benchmarks ...')

    for k in benchmarks:
        print('\n============ %s' % k.__name__)
        mins = []

        for func in k():
            if test_only:
                print(func.__name__, func())
            else:
                times =\
                    timeit.repeat('func()', setup='from __main__ import func')
                t = min(times)
                mins.append(t)

                print(func.__name__, t, times)
