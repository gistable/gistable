import socket

def get_host_name(s):
    for line in s.splitlines():
        if line.startswith('Host:'):
            return line[6:]
           

def host_to_ip(s):
    return socket.getaddrinfo(s, 80)[0][4][0]

def main():
    s_srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s_srv.bind(('127.0.0.1', 80))
    s_srv.listen(1)
    try:
        while True:
            conn, addr = s_srv.accept()
            print '---connected---'
            data = conn.recv(1024)
            print data
            print '-----client------'
            # proxy client
            ip = host_to_ip(get_host_name(data))
            s_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print ip
            s_cli.connect((ip, 80))
            s_cli.send(data)
            content = s_cli.recv(10240)
            s_cli.close()

            print content
            print '-----proxy-------'
            conn.send(content)
            conn.close()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
