# This code is in the public domain
# Author: Raphaël Barrois


from __future__ import print_function

import datetime
import mock


real_datetime_class = datetime.datetime

def mock_datetime_now(target, datetime_module):
    """Override ``datetime.datetime.now()`` with a custom target value.

    This creates a new datetime.datetime class, and alters its now()/utcnow()
    methods.

    Returns:
        A mock.patch context, can be used as a decorator or in a with.
    """

    # See http://bugs.python.org/msg68532
    # And http://docs.python.org/reference/datamodel.html#customizing-instance-and-subclass-checks
    class DatetimeSubclassMeta(type):
        """We need to customize the __instancecheck__ method for isinstance().

        This must be performed at a metaclass level.
        """

        @classmethod
        def __instancecheck__(mcs, obj):
            return isinstance(obj, real_datetime_class)

    class BaseMockedDatetime(real_datetime_class):
        @classmethod
        def now(cls, tz=None):
            return target.replace(tzinfo=tz)

        @classmethod
        def utcnow(cls):
            return target

    # Python2 & Python3-compatible metaclass
    MockedDatetime = DatetimeSubclassMeta('datetime', (BaseMockedDatetime,), {})

    return mock.patch.object(datetime_module, 'datetime', MockedDatetime)


def main():
    target = real_datetime_class(2009, 1, 1)

    print("Entering mock")
    with mock_datetime_now(target, datetime):
        print("- now                     ->", datetime.datetime.now())
        print("- isinstance(now, dt)     ->", isinstance(datetime.datetime.now(), datetime.datetime))
        print("- isinstance(target, dt)  ->", isinstance(target, datetime.datetime))


    print("Outside mock")
    print("- now                     ->", datetime.datetime.now())
    print("- isinstance(now, dt)     ->", isinstance(datetime.datetime.now(), datetime.datetime))
    print("- isinstance(target, dt)  ->", isinstance(target, datetime.datetime))


if __name__ == '__main__':
    main()
