import signal
import sys

def signal_term_handler(signal, frame):
    print 'got SIGTERM'
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_term_handler)