uwsgi.websocket_handshake(...)

user_id = get_user_id_from_environ(environ)

ready = gevent.event.Event()
dead = gevent.event.Event()

def ws_socket_waiter():
    while not dead.is_set():
        gevent.socket.wait_read(websocket_fd)
        ready.set()

def data_ready_waiter():
    while not dead.is_set():
        self.data_available_event.wait()
        ready.set()

gevent.spawn(ws_socket_waiter)
gevent.spawn(data_ready_waiter)

since = time.time()

try:
    while True:
        ready.wait(timeout=59)
        msg = uwsgi.websocket_recv_nb()
        if msg:
            logging.info('Received msg %s', msg)
            continue
        events = get_events_noblock_if_available(user_id, since)
        if events:
            logging.info('sending events')
            uwsgi.websocket_send(json.dumps({'updates': events}))
        since = time.time()
        ready.clear()
except IOError:
    pass
finally:
    dead.set()