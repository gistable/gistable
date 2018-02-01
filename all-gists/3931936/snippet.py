#!/usr/bin/env python
from optparse import OptionParser
from brod.zk import *
import pickle
import struct
import socket
import sys
import time


class Graphite:

    def __init__(self, host='localhost', port=2004, retry=5, delay=3, backoff=2, timeout=10):
        self.host = host
        self.port = port
        self.retry = retry
        self.delay = delay
        self.backoff = backoff
        self.timeout = timeout

        # Create initial socket
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.conn.settimeout(self.timeout)
        # Initiate connection
        self.connect()


    def _backoff(self, retry, delay, backoff):
        """Exponential backoff."""
        retry -= 1
        if retry == 0:
            raise Exception('Timeout')
        time.sleep(delay)
        delay *= backoff
        return retry, delay, backoff


    def _retry(self, exception, func, *args):
        """Retry calling the func catching a tuple of exceptions with backoff."""
        retry = self.retry
        delay = self.delay
        backoff = self.backoff
        while retry > 0:
            try:
                return func(*args)
            except exception, e:
                retry, delay, backoff = self._backoff(retry, delay, backoff)


    def connect(self):
        """Connect to graphite."""
        retry = self.retry
        backoff = self.backoff
        delay = self.delay
        while retry > 0:
            try:
                # Attempt to connect to Graphite, break if success
                self.conn.connect((self.host, self.port))
                break
            except socket.error, e:
                # Ditch this socket. Create a new one
                self.conn.close()
                self.conn.connect()
                retry, delay, backoff = self._backoff(retry, delay, backoff)


    def close(self):
        """Close connection go Graphite."""
        self.conn.close()


    def send(self, data, retry=3):
        """Send data to graphite."""
        retry = self.retry
        backoff = self.backoff
        delay = self.delay
        # Attempt to send any data in the queue
        while retry > 0:
            # Check socket
            if not self.conn:
                # Attempt to restablish connection
                self.close()
                self.connect()
                retry, delay, backoff = self._backoff(retry, delay, backoff)
                continue
            try:
                # Send data to socket
                self.conn.sendall(data)
                break
            except socket.error, e:
                self.close()
                self.connect()
                retry, delay, backoff = self._backoff(retry, delay, backoff)
                continue


def _pickle(batch):
    """Pickle metrics into graphite format."""
    payload = pickle.dumps(batch)
    header = struct.pack("!L", len(payload))
    message = header + payload
    return message


def _convert(msg):
    """Convert a graphite key value string to pickle."""
    path, timestamp, value = msg.split(' ')
    m = (path, (timestamp, value))
    return m


def _connect_zookeeper(zk, group, topic, autocommit=True):
    """Connect to ZooKeeper ensemble."""
    consumer = ZKConsumer(zk, group, topic, autocommit)
    return consumer


if __name__ == "__main__":
    batch = []

    parser = OptionParser()
    parser.add_option("-z", "--zk", dest="zookeeper", default="localhost:2181", help="Kafka ZooKeeper quorum")
    parser.add_option("-t", "--topic", dest="topic", help="Kafka topic")
    parser.add_option("-c", "--consumer", dest="consumer_group", default="graphite", help="Kafka consumer group")
    parser.add_option("-H", "--host", dest="graphite_host", default="localhost", help="Graphite host")
    parser.add_option("-p", "--port", dest="graphite_port", type=int, default=2004, help="Graphite port")
    parser.add_option("-k", "--pickle", dest="pickle_batch", action="store_true",  help="Pickle the graphite batches")
    parser.add_option("-b", "--batch", dest="batch_size", type=int, default=200, help="Graphite pickle batch size")
    parser.add_option("-i", "--interval", dest="poll", type=int, default=15, help="Poll interval for Kafaka topic")

    (options, args) = parser.parse_args()

    # Assign OptParse variables
    consumer_group = options.consumer_group
    topic = options.topic
    zookeeper = options.zookeeper
    batch_size = options.batch_size
    pickle_batch = options.pickle_batch
    host = options.graphite_host
    port = options.graphite_port
    poll = options.poll

    # Connect to Graphite
    try:
        graphite = Graphite(host, port)
    except socket.error, e:
        print "Could not connect to graphite host %s:%s" % (host, port)
        sys.exit(1)
    except socket.gaierror, e:
        print "Invalid hostname for graphite host %s" % (host)
        sys.exit(1)

    # Connect to ZooKeeper
    try:
        consumer = _connect_zookeeper(zookeeper, consumer_group, topic)
    except ZKConnectError, e:
        print "Could not connect to zookeeper ensemble %s" % (zookeeper)
        sys.exit(1)

    # Consume Kafka topic
    for msg_set in consumer.poll(poll_interval=poll):
        for offset, msg in msg_set:
            if pickle_batch:
                # Convert metric to Pickle format, and append batch
                batch.append(_convert(msg))
            else:
                # Append string to list
                batch.append(msg)
            # Check to see if we should send metrics to Graphite
            if len(batch) >= batch_size:
                # Pickle metrics if set to true
                if pickle_batch:
                    # Pickle graphite batch
                    pickled = _pickle(batch)
                    graphite.send(pickled)
                else:
                    # Send metrics to Graphite. Convert list to string
                    graphite.send("\n".join(batch))
                # Clear batch. Successfully sent
                print "Sent %s metrics to Graphite" % (len(batch))
                batch = []