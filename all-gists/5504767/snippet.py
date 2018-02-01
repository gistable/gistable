import socket, thread, sys
import logging

BUFLEN = 1024

logger = logging.getLogger(__name__)

class DLNAProxy(object):
    MEDIASERVER_IP = ""
    
    def __init__(self, connection, address, timeout):
        try:
            logger.debug("new connection handler")
        
            self.client = connection
            self.client_buffer = ''
            self.timeout = timeout
        
            # connect to target server
            (soc_family, _, _, _, address) = socket.getaddrinfo(self.MEDIASERVER_IP, 5001)[0]
            self.target = socket.socket(soc_family)
            self.target.connect(address)

            # get request
            request = "".join([part[1] for part in self.read_response(self.client)])
            request2 = request.replace("192.168.178.001", self.MEDIASERVER_IP)
            logger.debug("--------------------------------------------")
            logger.debug(request)
            logger.debug("--------------------------------------------")
        
            # send request to target server
            self.target.send(request2)
            
            # read response
            for text_content, response_part in self.read_response(self.target):
                if text_content:
                    self.client.send(response_part.replace(self.MEDIASERVER_IP, "192.168.178.001"))
                else:
                    self.client.send(response_part)

            self.client.close()
            self.target.close()
        except:
            logger.exception("Something went wrong")

    def read_response(self, read_socket):
        buffer = ""
        socket_file = read_socket.makefile()
        content_length = 0
        text_content = False
        while 1:
            line = socket_file.readline()
            buffer += line
            if "Content-Length" in line:
                content_length = int(line.split()[1])
            if "Content-Type" in line:
                text_content = "text/xml" in line
            if line == "\r\n":
                break
        logger.debug("Read header: %d", content_length)
        yield True, buffer
        if content_length > 1024*1024:
            data_part = socket_file.read(8*1024)
            while data_part:
                yield text_content, data_part
                data_part = socket_file.read(8*1024)
        else:
            yield text_content, socket_file.read(content_length)

class DLNAMulticastHelper(object):
    MCAST_GRP = '239.255.255.250'
    MCAST_PORT = 1900
    
    def __init__(self, mediaserver_ip):
        self.mediaserver_ip = mediaserver_ip
    
    def run(self):
        sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock_send.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock_send.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_send.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton("192.168.178.1"))

        sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock_recv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_recv.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(self.MCAST_GRP)+socket.inet_aton("192.168.179.1"))
        sock_recv.bind((self.MCAST_GRP, self.MCAST_PORT))

        while True:
            dgram, addr = sock_recv.recvfrom(10240)
            dgram2 = dgram.replace(self.mediaserver_ip, "192.168.178.1")
            sock_send.sendto(dgram2, (self.MCAST_GRP, self.MCAST_PORT))


if __name__ == '__main__':
    logging.basicConfig()

    # start multicast helper
    multi_helper = DLNAMulticastHelper(sys.argv[1])
    thread.start_new_thread(multi_helper.run, tuple())

    # start HTTP proxy
    DLNAProxy.MEDIASERVER_IP = sys.argv[1]
    soc = socket.socket(socket.AF_INET)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind(("192.168.178.1", 5001))
    soc.listen(0)
    while 1:
        thread.start_new_thread(DLNAProxy, soc.accept()+(60,))