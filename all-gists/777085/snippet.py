import sys
import gevent
from gevent.monkey import patch_all; patch_all()
from gevent import server, event, socket
from multiprocessing import Process, current_process, cpu_count

"""
Simple multiprocess StreamServer that proxies messages between clients.

Avoids using a multiprocessing.Event since it blocks on a semaphore.

"""

def note(format, *args):
    sys.stderr.write('[%s]\t%s\n' % (current_process().name, format%args))

class ChatHandler(object):
    
    def __init__(self, main_location):
        self._main_location = main_location
        self.green_event = event.Event()
        self.messages = []
        gevent.spawn_later(1, self.communicate_with_main)

    def add_message(self, author, message):
        note('%s: %s' % (author, message))
        self.main_socket.send('From %s %s > %s \r\n' % (author, current_process().name, message))

    def communicate_with_main(self):
        self.main_socket = socket.create_connection(self._main_location)
        f = self.main_socket.makefile()
        while True:
            m = f.readline()
            if not m:
                note('client disconnected')
                break

            self.messages.append(m)
            self.green_event.set()
            self.green_event.clear()
                
    def wait_for_green_events(self, fileobj):
        print 'wait for green'
        idx = len(self.messages)
        while True:
            self.green_event.wait()
            try:
                for message in self.messages[idx:]:
                    fileobj.write('> '+ message)
                fileobj.flush()
                idx = len(self.messages)
            except:
                print 'error writing to a client'
                break
            

    def handle(self, fileobj, address):
        while True:
            note('reading from client')
            line = fileobj.readline()
            if not line:
                print "client disconnected"
                break
            if line.strip().lower() == 'quit':
                print "client quit"
                break
            
            self.add_message(address, line)

        fileobj.close()

    def __call__(self, socket, address):
        print 'New connection from %s:%s' % address
    
        fileobj = socket.makefile()
        fileobj.write('Welcome to the chat server! Type quit to exit.\r\n')
        fileobj.write('In %s\n\n' % current_process().name)
        fileobj.flush()
        
        gevent.spawn(self.wait_for_green_events, fileobj)
        gevent.spawn(self.handle, fileobj, address).join()


class main(object):
    
    def __init__(self):
        self.children = []

    def __call__(self, socket, address):
        self.children.append((socket, address))
        gevent.spawn(self.listen, socket, address)

    def write_to_children(self, author, message):
        print 'writing message to children', message, len(self.children)
        for c in self.children:
            print 'sending to', c
            gevent.spawn(c[0].send, message)
        
    def listen(self, socket, address):
        f = socket.makefile()
        while True:
            line = f.readline()
            if not line:
                print 'client died'
                break
            self.write_to_children(address, line)
    

main_listen = ('127.0.0.1', 4002)
main = server.StreamServer(main_listen, main())

Chat = ChatHandler(main_listen)

s = server.StreamServer(('127.0.0.1', 4001), Chat)
s.pre_start()

def serve_forever(server, main_listen):
    Chat = ChatHandler(main_listen)
    server.set_handle(Chat)
    try:
        gevent.spawn_later(1, server.start_accepting)
        try:
            server._stopped_event.wait()
        except:
            raise
    except KeyboardInterrupt:
        pass

number_of_processes = cpu_count() - 1
number_of_processes = 2
print 'Starting %s processes' % number_of_processes
processes = [Process(target=serve_forever, args=(s, main_listen)) for i in range(number_of_processes)]


for process in processes:
    process.start()
s.start()
main.start()

gevent.joinall([main._stopped_event, s._stopped_event])
