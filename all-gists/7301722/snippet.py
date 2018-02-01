"""
Install twisted (pip install twisted) and PIL (pip install PIL), and run the script.

On your gateway, run the following commands:
iptables -t nat -A PREROUTING -i br0 -s ! 192.168.0.20 -p tcp --dport 80 -j DNAT --to 192.168.0.20:8080
iptables -t nat -A POSTROUTING -o br0 -s 192.168.0.0/24 -d 192.168.0.20 -j SNAT --to 192.168.0.1
iptables -A FORWARD -s 192.168.0.0/24 -d 192.168.0.20 -i br0 -o br0 -p tcp --dport 8080 -j ACCEPT

Substitute 192.168.0.20 for the computer running the proxy.
"""
from twisted.internet import reactor
from twisted.web import proxy, http
from PIL import Image
import StringIO
import zlib

img = Image.open("hoff.png")

class LoggingProxyClient(proxy.ProxyClient):
    def __init__(self, command, rest, version, headers, data, father):
        del headers["accept-encoding"]
        proxy.ProxyClient.__init__(self, command, rest, version, headers, data, father)
        self.isImage = False
        self.isHtml = False
        self.buffer = ""

    def handleStatus(self, version, code, message):
        proxy.ProxyClient.handleStatus(self, version, code, message)

    def handleHeader(self, key, value):
        if key.lower() == "content-type" and value.startswith("image/"):
            self.isImage = True
            self.isHtml = False
            self.imageType = value
        elif key.lower() == "content-type" and value.startswith("text/html"):
            self.isHtml = True
            self.isImage = False

        proxy.ProxyClient.handleHeader(self, key, value)

    def handleResponsePart(self, buffer):
        #proxy.ProxyClient.handleResponsePart(self, buffer)
        self.buffer += buffer

    def handleResponseEnd(self):
        if not self._finished:
            if self.isImage:
                try:
                    oldBuffer = StringIO.StringIO(self.buffer)
                    oldImg = Image.open(oldBuffer)

                    w, h = oldImg.size
                    if w > 50 and h > 50 and w >= h:
                        print "Inserting the hoff into image of size: ", str(oldImg.size)

                        nh = h/2
                        nw = nh * img.size[0] / img.size[1]

                        mask = Image.new("RGBA", oldImg.size)
                        maskData = mask.load()
                        for x in xrange(0, w):
                            for y in xrange(0, h):
                                maskData[x, y] = (0xFF, 0xFF, 0xFF, 0xFF)

                        newImg = oldImg.copy().convert("RGBA")
                        pasteImg = img.copy().resize((nw, nh))
                        newImg = Image.blend(newImg, mask, 0.5)
                        newImg.paste(pasteImg, (w - nw, h - nh), pasteImg)

                        newBuffer = StringIO.StringIO()
                        if self.imageType == "image/png":
                            newImg.save(newBuffer, "PNG")
                        elif self.imageType in ("image/jpg", "image/jpeg"):
                            newImg.save(newBuffer, "JPEG")

                        self.buffer = newBuffer.getvalue()

                        self.father.responseHeaders.setRawHeaders("Cache-Control", ["no-cache"])
                except Exception as e:
                    print repr(e)
            elif self.isHtml:
                print "Hoffifying HTML"
                #try:
                #    newBuffer = zlib.decompress(self.buffer)
                #except:
                #    newBuffer = self.buffer

                newBuffer = self.buffer
                self.buffer = newBuffer \
                                  .replace("He ", " The Hoff ") \
                                  .replace("She ", " The Hoff ") \
                                  .replace("Jag", " The Hoff ") \
                                  .replace("Han ", " The Hoff ") \
                                  .replace("han ", " The Hoff ") \
                                  .replace("Honom", " The Hoff ") \
                                  .replace("honom", " The Hoff ") \
                                  .replace("Hon ", " The Hoff ") \
                                  .replace("hon ", " The Hoff ") \
                                  .replace("Henne", " The Hoff ") \
                                  .replace("henne", " The Hoff ")
                #print self.buffer

            self.father.responseHeaders.setRawHeaders("Content-Length", [str(len(self.buffer))])
            self.father.write(self.buffer)
            proxy.ProxyClient.handleResponseEnd(self)

class LoggingProxyClientFactory(proxy.ProxyClientFactory):
    protocol = LoggingProxyClient

class LoggingProxyRequest(proxy.ProxyRequest):
    protocols = { "http": LoggingProxyClientFactory }

    def process(self):
        # when the client isn't aware it's talking to a proxy, it won't send
        # the full path to the web server. here we prepend http:// and the server
        # host to the uri
        if not self.uri.startswith("http://") and not self.uri.startswith("https://"):
            self.uri = "http://" + self.getHeader("Host") + self.uri
        print "Request from %s for %s" % (self.getClientIP(), self.uri)
        try:
            proxy.ProxyRequest.process(self)
        except KeyError:
            print "HTTPS is not supported at the moment!"

class LoggingProxy(proxy.Proxy):
    requestFactory = LoggingProxyRequest

class LoggingProxyFactory(http.HTTPFactory):
    def buildProtocol(self, addr):
        return LoggingProxy()

reactor.listenTCP(8080, LoggingProxyFactory())
reactor.run()
