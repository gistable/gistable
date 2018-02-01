import datetime as dt
import time
import unittest


def aws_age_seconds(ec2_launch_time):
    """
    Parse the ec2 launch time string and return how old it is in seconds.
    """
    # Strip trailing subsecond part
    ec2_launch_time = ec2_launch_time[:-len('.000Z')]
    launch_time_tuple = time.strptime(ec2_launch_time, "%Y-%m-%dT%H:%M:%S")
    launch_time_dt = dt.datetime(*launch_time_tuple[:6])
    seconds_diff = (dt.datetime.utcnow() - launch_time_dt).total_seconds()
    return seconds_diff


def filter_prefix(items, prefix):
    return [x for x in items if x.startswith(prefix)]


class FilterModule(object):
    def filters(self):
        return {
            'aws_age_seconds': aws_age_seconds,
            'filter_prefix': filter_prefix,
        }


if __name__ == '__main__':
    # Import freezegun here so ansible can run without it installed
    from freezegun import freeze_time

    class FilterTests(unittest.TestCase):

        @freeze_time('2014-10-02T01:01:01')
        def test_aws_age_seconds(self):
            age = aws_age_seconds
            self.assertEqual(age('2014-10-01T12:57:35.000Z'), 43406.0)
            self.assertEqual(age('2014-10-01T12:57:35.303Z'), 43406.0)
            self.assertEqual(age('2014-10-02T01:01:01.000Z'), 0.0)

    unittest.main()
