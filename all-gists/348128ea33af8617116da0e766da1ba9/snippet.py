# An example of using SQLAlchemy / PSQL for PubSub with asyncio
# Rather than using `select.select` to watch for messages, we use
# `loop.add_reader`.
# Inspired by: https://gist.github.com/dtheodor/3862093af36a1aeb8104
#
# One example of use is with aiopyramid.
#
# For an additional consideration, read about case folding here:
# http://stackoverflow.com/a/5173993/465164

import asyncio
from datetime import datetime
import threading
from time import sleep

from sqlalchemy import (
    create_engine,
    text,
)
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)


def log(msg, prefix=''):
    print('{}[{}] {}'.format(
        prefix,
        datetime.now(),
        msg
    ), flush=True)


def pg_subscribe(conn, *channels):

    cmd = ' '.join(['LISTEN "{}";'.format(channel) for channel in channels])
    conn.execute(text(cmd))
    conn.connection.poll()
    log(cmd)


def pg_unsubscribe(conn, *channels):
    cmd = ' '.join(['UNLISTEN "{}";'.format(channel) for channel in channels])
    conn.execute(text(cmd))
    log(cmd)


def pg_notified(conn):
    conn.connection.poll()
    while conn.connection.notifies:
        notify = conn.connection.notifies.pop(0)
        log("Got NOTIFY: {} '{}' on {}".format(
            notify.channel,
            notify.payload,
            notify.pid,
        ))


def get_conn(session):
    conn = session.bind.connect().execution_options(autocommit=True)
    conn.detach()  #  because we're applying non-default settings
    return conn


def test_notify(session, *channels):
    for i in range(5):
        for channel in channels:
            msg = "'msg{}'".format(i)
            cmd = 'NOTIFY {}, {}'.format(channel, msg)
            session.execute(text(cmd))
            log("Put NOTIFY: {} {}".format(channel, msg))
            session.commit()


def loop_in_thread(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


if __name__ == '__main__':
    # Set up sqla
    engine = create_engine('postgresql://chaizen@postgres/chaizen')
    session = scoped_session(sessionmaker())
    session.configure(bind=engine)
    # perhaps bind it to a Pyramid or Flask request here...

    channels = ['test1', 'test2']
    ps_conn = get_conn(session)

    loop = asyncio.get_event_loop()
    loop.add_reader(ps_conn.connection, pg_notified, ps_conn)
    t = threading.Thread(target=loop_in_thread, args=(loop,))
    t.start()

    # Demo Subscribe
    log('Demo Subscribe', prefix='\n')
    pg_subscribe(ps_conn, *channels)
    test_notify(session, *channels)
    pg_unsubscribe(ps_conn, '*', True)
    sleep(1)

    # Demo Unsubscribe
    log('Demo Unsubscribe', prefix='\n')
    pg_subscribe(ps_conn, *channels)
    pg_unsubscribe(ps_conn, *channels)
    test_notify(session, *channels)

# Outputs
# [2016-10-16 10:28:17.976968] Demo Subscribe
# [2016-10-16 10:28:17.980379] LISTEN "test1"; LISTEN "test2";
# [2016-10-16 10:28:17.996296] Put NOTIFY: test1 'msg0'
# [2016-10-16 10:28:18.004493] Got NOTIFY: test1 'msg0' on 20763
# [2016-10-16 10:28:18.006828] Put NOTIFY: test2 'msg0'
# [2016-10-16 10:28:18.011654] Got NOTIFY: test2 'msg0' on 20763
# [2016-10-16 10:28:18.012671] Put NOTIFY: test1 'msg1'
# [2016-10-16 10:28:18.014374] Got NOTIFY: test1 'msg1' on 20763
# [2016-10-16 10:28:18.016014] Put NOTIFY: test2 'msg1'
# [2016-10-16 10:28:18.018401] Got NOTIFY: test2 'msg1' on 20763
# [2016-10-16 10:28:18.018937] Put NOTIFY: test1 'msg2'
# [2016-10-16 10:28:18.021849] Put NOTIFY: test2 'msg2'
# [2016-10-16 10:28:18.022143] Got NOTIFY: test1 'msg2' on 20763
# [2016-10-16 10:28:18.023516] Got NOTIFY: test2 'msg2' on 20763
# [2016-10-16 10:28:18.025725] Put NOTIFY: test1 'msg3'
# [2016-10-16 10:28:18.028685] Put NOTIFY: test2 'msg3'
# [2016-10-16 10:28:18.032518] Put NOTIFY: test1 'msg4'
# [2016-10-16 10:28:18.036229] Got NOTIFY: test1 'msg3' on 20763
# [2016-10-16 10:28:18.036786] Put NOTIFY: test2 'msg4'
# [2016-10-16 10:28:18.037756] Got NOTIFY: test2 'msg3' on 20763
# [2016-10-16 10:28:18.039980] Got NOTIFY: test1 'msg4' on 20763
# [2016-10-16 10:28:18.040858] UNLISTEN "*"; UNLISTEN "True";
#
# [2016-10-16 10:28:19.047260] Demo Unsubscribe
# [2016-10-16 10:28:19.051156] Got NOTIFY: test2 'msg4' on 20763
# [2016-10-16 10:28:19.051949] LISTEN "test1"; LISTEN "test2";
# [2016-10-16 10:28:19.053829] UNLISTEN "test1"; UNLISTEN "test2";
# [2016-10-16 10:28:19.055745] Put NOTIFY: test1 'msg0'
# [2016-10-16 10:28:19.057999] Put NOTIFY: test2 'msg0'
# [2016-10-16 10:28:19.059819] Put NOTIFY: test1 'msg1'
# [2016-10-16 10:28:19.061526] Put NOTIFY: test2 'msg1'
# [2016-10-16 10:28:19.063143] Put NOTIFY: test1 'msg2'
# [2016-10-16 10:28:19.064714] Put NOTIFY: test2 'msg2'
# [2016-10-16 10:28:19.066341] Put NOTIFY: test1 'msg3'
# [2016-10-16 10:28:19.067955] Put NOTIFY: test2 'msg3'
# [2016-10-16 10:28:19.069549] Put NOTIFY: test1 'msg4'
# [2016-10-16 10:28:19.071197] Put NOTIFY: test2 'msg4'