#!/usr/bin/env python2
import logging

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from multiprocessing.pool import ThreadPool
from multiprocessing import cpu_count
import libemu
from cachetools import LRUCache
from scapy.layers.all import TCP, UDP, Raw
from scapy.all import sniff
import Queue


stream_cache = LRUCache(1024)
BUFFER_SIZE = 1024 * 1024
USE_SLIDING_WINDOW = True
THREADS = cpu_count()
thread_pool = None


class LimitedPool(ThreadPool):
    def __init__(self, processes=None, initializer=None, initargs=(), max_queue_size=10000):
        self._max_queue_size = max_queue_size
        ThreadPool.__init__(self, processes, initializer, initargs)

    def _setup_queues(self):
        self._inqueue = Queue.Queue(self._max_queue_size)
        self._outqueue = Queue.Queue()
        self._quick_put = self._inqueue.put
        self._quick_get = self._outqueue.get


def generate_key(packet):
    k = "{0}:{1}-{2}:{3}".format(packet.payload.src, packet.payload.payload.sport, packet.payload.dst, packet.payload.payload.dport)
    if packet.haslayer(TCP):
        return "tcp://{0}".format(k)
    if packet.haslayer(UDP):
        return "udp://{0}".format(k)


def test_for_shellcode((key, packet, file_path)):
    e = libemu.Emulator()
    r = e.test(packet)
    if r is not None and r >= 0:
        logging.warning("{2}: {0} - {1}".format(key, {"offset": r}, file_path))


def process_packet(pkt, file_path):
    global thread_pool
    try:
        if pkt.haslayer(Raw) and len(pkt[Raw].original) > 0:
            k = generate_key(pkt)
            if USE_SLIDING_WINDOW:
                if k in stream_cache:
                    stream_cache[k] += pkt[Raw].original
                    stream_cache[k] = stream_cache[k][-BUFFER_SIZE:]
                else:
                    stream_cache[k] = pkt[Raw].original[-BUFFER_SIZE:]
                p = stream_cache[k]
            else:
                p = pkt[Raw].original

            #test_for_shellcode((k, p, file_path))
            thread_pool.apply_async(test_for_shellcode, [(k, p, file_path)])
    except KeyboardInterrupt:
        raise
    except:
        pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    from argparse import ArgumentParser

    parser = ArgumentParser(
        prog=__file__,
        description="Proof of concept for shellcode identification in pcap or network",
        version="%(prog)s v0.0.1 by Brian Wallace (@botnet_hunter)",
        epilog="%(prog)s v0.0.1 by Brian Wallace (@botnet_hunter)"
    )
    parser.add_argument('path', metavar='path', type=str, nargs='*', default=None, help="Paths to files to parse")

    args = parser.parse_args()

    thread_pool = LimitedPool(processes=THREADS, max_queue_size=200)

    if args.path is None or len(args.path) == 0:
        print "Live sniffing"
        sniff(store=0, filter="tcp or udp", prn=lambda x: process_packet(x, "live"))
    else:
        for p in args.path:
            logging.warning("Reading packets from {0}".format(p))
            sniff(store=0, filter="tcp or udp", offline=p, prn=lambda x: process_packet(x, p))

    thread_pool.close()
    thread_pool.join()