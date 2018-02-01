import daemon, lockfile, signal, logging

import eventlet
from eventlet import wsgi, timeout

worker_pool = eventlet.GreenPool(20)
sock = eventlet.listen(('', 8000))

def proper_shutdown():
    worker_pool.resize(0)
    sock.close()
    logging.info("Shutting down. Requests left: %s", worker_pool.running())
    worker_pool.waitall()
    logging.info("Exiting.")
    raise SystemExit()

def queue_shutdown(signal_number, stack_frame):
    eventlet.spawn_n(proper_shutdown)

def test_app(evn, start_response):
    start_response('200 OK', {})
    eventlet.sleep(20)
    return ['hi']

# Daemon things

context = daemon.DaemonContext(
    working_directory='.',
    umask=0o002,
    pidfile=lockfile.FileLock('shutdown-example.pid'),
)

context.signal_map = {
    signal.SIGTERM: queue_shutdown,
}

context.files_preserve = [sock]

with context:
    logging.basicConfig(filename='shutdown.log', level=logging.INFO)
    logging.info("Starting")
    wsgi.server(sock, test_app, custom_pool=worker_pool)
