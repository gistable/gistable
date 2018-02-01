# coding=utf-8
import sys
import socket
import select
from urlparse import urlparse, parse_qs
import word2vec

argvs = sys.argv

port = 8000
#第二引数は、ポート番号(デフォルト8000)
if argvs[2]:
     port = int(argvs[2])

#第一引数のモデルファイルをロード
if not argvs[1]:
     print "Not found model file path"
     exit(1)

print "loading model"
model=word2vec.load(argvs[1])
print "done"

read_waits = {}
write_waits = {}

def wait_read(con, callback):
    read_waits[con.fileno()] = callback

def wait_write(con, callback):
    write_waits[con.fileno()] = callback

def evloop():
    while 1:
        rs, ws, xs = select.select(read_waits.keys(), write_waits.keys(), [])
        for rfd in rs:
            read_waits.pop(rfd)()
        for wfd in ws:
            write_waits.pop(wfd)()

class Server(object):
    def __init__(self, con):
        self.con = con

    def start(self):
        wait_read(self.con, self.on_acceptable)

    def on_acceptable(self):
        try:
            while 1:
                con, _ = self.con.accept()
                con.setblocking(0)
                Client(con)
        except IOError:
            wait_read(self.con, self.on_acceptable)


class Client(object):
    def __init__(self, con):
        self.con = con
        self.on_readable()

    def on_readable(self):
        data = self.con.recv(32 * 1024)
        if not data:
            wait_read(self.con, self.on_readable)
            return

        # GET値に応じて、(c=類語,pos,neg=アナロジー,n=取得数)を取得する
        content = ""
        content_len = 0
        sp_data = data.split(' ',2)
        if sp_data[0] == 'GET':
            parse_query = parse_qs(urlparse(sp_data[1]).query)
            n = 5
            if parse_query.has_key("n"):
                n = int(parse_query['n'][0].split(' ')[0])
            if parse_query.has_key("c"):
                sp_parse = parse_query['c'][0].split(' ')
                try:
                    content = model.cosine(sp_parse, n=n)
                    content = content[sp_parse[0]]
                    content_str = map(str,content)
                    content = ",".join(content_str)
                    content = content.replace('(','')
                    content = content.replace(')','')
                    content = content.replace("', ","' : ")
                    content = content.replace("'",'"')
                    content = content.decode('string-escape')
                    content = "{" + content + "}"
                except:
                    content = '{"Not found":"Not found word in model data"}'
                content_len = len(content) + 1
            elif parse_query.has_key("pos") and parse_query.has_key("neg"):
                pos_parse = parse_query['pos'][0].split(' ')
                neg_parse = parse_query['neg'][0].split(' ')

                try:
                    content = model.analogy(pos=pos_parse, neg=neg_parse, n=n)
                    content = content
                    content_str = map(str,content)
                    content = ",".join(content_str)
                    content = content.replace('(','')
                    content = content.replace(')','')
                    content = content.replace("', ","' : ")
                    content = content.replace("'",'"')
                    content = content.decode('string-escape')
                    content = "{" + content + "}"
                except:
                    content = '{"Not found":"Not found word in model data"}'
                content_len = len(content) + 1

        if content_len == 0:
            self.buf = b"""HTTP/1.1 404 Not Found"""
        else:
            self.buf = b"""HTTP/1.1 200 OK\r
Content-Type: application/json\r
Content-Length: %d\r
\r
%s
""" % (content_len,content)

        self.on_writable()

    def on_writable(self):
        wrote = self.con.send(self.buf)
        self.buf = self.buf[wrote:]
        if self.buf:
            wait_write(self.con, self.on_writable)
        else:
            self.con.close()


def serve():
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(0)
    sock.bind(('', port))
    sock.listen(128)
    server = Server(sock)
    server.start()
    evloop()

if __name__ == '__main__':
    serve()