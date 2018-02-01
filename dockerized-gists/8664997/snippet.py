import zmq


DEFAULT_PAGE = '\r\n'.join([
    "HTTP/1.0 200 OK",
    "Content-Type: text/plain",
    "",
    "Hello, World!",
])


context = zmq.Context()

router = context.socket(zmq.ROUTER)
router.router_raw = True
router.bind('tcp://*:8080')

while True:
    msg = router.recv_multipart()
    identity, request = msg

    # send Hello World page
    router.send_multipart([identity, DEFAULT_PAGE])
    # Close connection to browser
    router.send_multipart([identity, ''])
