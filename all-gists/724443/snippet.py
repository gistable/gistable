# based on http://amix.dk/blog/post/19574
from datetime import datetime, timedelta


GRAVITY = 0.5  # HN default: 1.8
WINDOW = 36  # max age in hours
now = datetime.now()


def hours_from_dt(dt):
    delta = now - dt
    hrs = 0
    if delta.days > 0:
        hrs = delta.days * 24
    hrs += delta.seconds / 3600
    return hrs


def score(age, gravity=GRAVITY):
    hour_age = hours_from_dt(age)
    if hour_age > WINDOW:
        return 0
    else:
        return 1 / pow((hour_age + 1), gravity)


def test(gravity=GRAVITY):
    hours = [now - timedelta(hours=x) for x in range(0, 48)]
    for h in hours:
        print "Hour %s, 1 == %s" % (h, score(h, gravity))
