import sys
import tornado.ioloop
import psycopg2
import psycopg2.extensions

io_loop = tornado.ioloop.IOLoop.instance()
conn = psycopg2.connect('dbname=mytest user=lbolla password=secret')
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)


def listen(ch):
    '''Listen to a channel.'''
    curs = conn.cursor()
    curs.execute("LISTEN %s;" % ch)


def receive(fd, events):
    '''Receive a notify message from the channel we are listening.'''
    state = conn.poll()
    if state == psycopg2.extensions.POLL_OK:
        if conn.notifies:
            notify = conn.notifies.pop()
            print(notify.payload)
io_loop.add_handler(conn.fileno(), receive, io_loop.READ)


def talk(who, ch):
    # Connections are thread-safe, but cursors are not
    curs = conn.cursor()

    def _talk():
        while True: 
            what = input()
            msg = '[%s] %s: %s' % (ch, who, what)
            # Notify all of what you just said
            curs.execute("NOTIFY %s, '%s';" % (ch, msg))
    # Run in a separate thread: we could also monitor stdin into the IOLoop...
    threading.Thread(target=_talk).start()


if __name__ == '__main__':
    who, ch = sys.argv[1:3]
    # Always listen before talk!
    listen(ch)
    talk(who, ch)
    io_loop.start()
