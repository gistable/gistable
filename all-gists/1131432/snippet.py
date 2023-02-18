import multiprocessing

# The socket to bind.
bind = "127.0.0.1:8080"
# The maximum number of pending connections.
backlog = 2024
# The number of worker process for handling requests
workers = multiprocessing.cpu_count() * 2 + 1
# The type of workers to use. (sync|eventlet|gevent|tornado)
worker_class = 'gevent'
# The maximum number of simultaneous clients.
worker_connections = 1000
# The maximum number of requests a worker will process before restarting
max_requests =  1000
# Workers silent for more than this many seconds are killed and restarted.
timeout = 30
# The number of seconds to wait for requests on a Keep-Alive connection.
keepalive = 1
# Turn on debugging in the server
# This limits the number of worker processes to 1 and changes some error handling that's sent to clients
debug = False
# Install a trace function that spews every line executed by the server.
spew = False
# Load application code before the worker processes are forked.
preload_app = False
# Daemonize the Gunicorn process.
daemon = False
# A filename to use for the PID file.
pidfile = '/tmp/gunicorn.pid'
# Switch worker processes to run as this user.
#user = 'user'
# Switch worker process to run as this group.
#group = 'group'
# A bit mask for the file mode on files written by Gunicorn.
umask = 0
# Directory to store temporary request data as they are read
tmp_upload_dir = None
# The log file to write to
logfile = '/var/log/gunicorn.log'
# The granularity of log outputs. (debug|info|warning|error|critical)
loglevel = 'debug'
#The log config file to use.
logconfig = None
# A base to use with setproctitle for process naming.
proc_name = 'gunicorn'
# Internal setting that is adjusted for each type of application.
default_proc_name = 'gunicorn'

# Called just before the main process is initialized.
def on_starting(server):
    pass

# Called just after the server is started.
def when_ready(server):
    pass

# Called just before a worker is forked.
def pre_fork(server, worker):
    pass

# Called just after a worker has been forked.
def post_fork(server, worker):
    pass

# Called just before a new main process is forked.
def pre_exec(server):
    pass

# Called just before a worker processes the request.
def pre_request(worker, req):
    worker.log.debug("%s %s" % (req.method, req.path))

# Called after a worker processes the request.
def post_request(worker, req):
    pass

# Called just after a worker has been exited.
def worker_exit(server, worker):
    pass