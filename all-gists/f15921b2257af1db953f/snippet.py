
# reuse freely

from datetime import datetime, timezone, timedelta

# usage: naturaltime.to_text(some_datetime)

def past(dt, dif):

    if dif.days > 2:
        return '%d days ago' % int(dif.days)
    
    if dif.days > 1:
        return 'yesterday at %s' % dt.strftime('%I:%M %p')

    if dif.seconds <= 60:
        return '%d seconds ago' % int(dif.seconds)

    if dif.seconds <= (60 * 10):
        return '%d minutes, %d seconds ago' % \
            (int(dif.seconds / 60), int(dif.seconds) % 60)

    if dif.seconds <= (60 * 60):
        return 'about %d minutes ago' % int(dif.seconds / 60)

    return '%d hours, %d minutes ago' % \
        (int(dif.seconds / (60 * 60)), int(dif.seconds / 60) % 60)


def future(dt, dif):
    if dif.days > 2:
        return 'in %d days time' % int(dif.days)
    
    if dif.days > 1:
        return 'tomorrow at %s' % dt.strftime('%I:%M %p')

    if dif.seconds <= 60:
        return '%d seconds from now' % int(dif.seconds)

    if dif.seconds <= (60 * 10):
        return '%d minutes, %d seconds from now' % \
            (int(dif.seconds / 60), int(dif.seconds) % 60)

    if dif.seconds <= (60 * 60):
        return 'about %d minutes from now' % int(dif.seconds / 60)

    return '%d hours, %d minutes from now' % \
        (int(dif.seconds / (60 * 60)), int(dif.seconds / 60) % 60)


def to_text(dt):
    now = datetime.now(timezone.utc)
    dif = dt - now
    smalld = timedelta(seconds=5)
    
    if dif < smalld:
        if abs(dif) < smalld: return 'just now'
        return past(dt, abs(dif))
    else:
        if abs(dif) < smalld: return 'now'
        return future(dt, abs(dif))
