class myHTTPTransport(HTTPTransport):
    """
    Bastardized HTTP Transport that lets us override the port and protocol info from
    the WSDL.  (Sometimes it wants us to talk over port 9080 with http...)
    Found many versions of this on the net, but cleaned this one up and added my overrides
    """

    username = None
    passwd = None
    protocol = None
    port = None

    @classmethod
    def setAuthentication(cls,u,p):
        cls.username = u
        cls.passwd = p

    @classmethod
    def setProtocol(cls,proto,port):
        cls.protocol = proto
        cls.port = port

    def call(self, addr, data, namespace, soapaction=None, encoding=None,
             http_proxy=None, config=Config, timeout=-1):

        if not isinstance(addr, SOAPAddress):
            addr=SOAPAddress(addr, config)

        if self.protocol != None:
            if ':' in addr.host:
                host,port = addr.host.split(':')
                addr.host = addr.host.replace(':'+port,':'+self.port)
            else:
                addr.host = add.host+":"+self.port

            addr.proto = self.protocol

        if self.username != None:
            addr.user = self.username+":"+self.passwd


        return HTTPTransport.call(self, addr, data, namespace, soapaction,
                                  encoding, http_proxy, config, timeout)
