def try_connect(ip, port, return_value):
    sock = socket.socket()
    try:
        sock.connect((ip, port))
    except ConnectionRefusedError:
        pass
    else:
        return_value[0] = sock


def multiconnect(ip, port, ports_range=5):
    threads = []
    connected_socket = [None]
    for z in range(ports_range):
        threads.append(
            threading.Thread(
                target=try_connect,
                args=(ip, port+z, connected_socket)
            )
        )
        threads[z].start()

    while any(list(map(lambda x: x.is_alive(), threads))):
        time.sleep(0.05)

    return connected_socket[0]
