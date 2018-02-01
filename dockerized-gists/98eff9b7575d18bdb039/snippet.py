import zmq
import time
from multiprocessing import Process
import numpy as np
from pprint import pprint
import json

np.set_printoptions(precision=3)


def send_arrays(socket, array_payload, flags=0, copy=True, track=False):
    """send a numpy array with metadata"""

    names = sorted(array_payload.keys())
    md = []
    payload = []

    for name in names:
        data = array_payload[name]

        md.append(dict(dtype=str(data.dtype),
                       shape=data.shape,
                       name=name))

        payload.append(data)

    # Send the header
    p1 = json.dumps(md)

    return socket.send_multipart([p1] + payload, flags, copy=copy, track=track)


def recv_arrays(socket, flags=0, copy=True, track=False):
    """recv a numpy array"""

    results = dict()

    msg = socket.recv_multipart(flags=flags)

    md_array = json.loads(msg[0])

    for i, md in enumerate(md_array, start=1):
        buf = buffer(msg[i])

        results[md['name']] = np.frombuffer(buf, dtype=md['dtype'])
        results[md['name']].shape = md['shape']

    return results


def server(port="5556"):
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://*:%s" % port)
    print "Running server on port: ", port
    # serves only 5 request and dies
    for reqnum in range(5):
        # Wait for next request from client
        message = recv_arrays(socket)
        print "Received request #%s" % reqnum
        pprint(message)


def client(ports=["5556"]):

    context = zmq.Context()
    print "Connecting to server with ports %s" % ports
    socket = context.socket(zmq.PAIR)

    for port in ports:
        socket.connect("tcp://localhost:%s" % port)

    for request in range(5):
        print "Sending request ", request, "..."
        send_arrays(socket, dict(x=np.random.randn(5, 2),
                                 y=np.random.randint(0, 2, size=5)))

        time.sleep(1)


if __name__ == "__main__":
    # Now we can run a few servers
    server_ports = [5550]

    for server_port in server_ports:
        Process(target=server, args=(server_port,)).start()

    # Now we can connect a client to all these servers
    Process(target=client, args=(server_ports,)).start()
