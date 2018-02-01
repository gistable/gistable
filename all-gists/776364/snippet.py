import sys
from gevent import server
from multiprocessing import Process, current_process, cpu_count


def note(format, *args):
    sys.stderr.write('[%s]\t%s\n' % (current_process().name, format%args))

def echo(socket, address):
    print 'New connection from %s:%s' % address
    fileobj = socket.makefile()
    fileobj.write('Welcome to the echo server! Type quit to exit.\r\n')
    fileobj.write('In %s\r\n' % current_process().name)
    fileobj.flush()
    while True:
        line = fileobj.readline()
        if not line:
            print "client disconnected"
            break
        if line.strip().lower() == 'quit':
            print "client quit"
            break
        fileobj.write(current_process().name + '\t' + line)
        fileobj.flush()
        print "echoed", repr(line)

s = server.StreamServer(('127.0.0.1', 8001), echo)
s.pre_start()

def serve_forever(server):
    note('starting server')
    try:
        server.start_accepting()
        try:
            server._stopped_event.wait()
        except:
            raise
    except KeyboardInterrupt:
        pass
    
number_of_processes = cpu_count() - 1
print 'Starting %s processes' % number_of_processes
for i in range(number_of_processes):
    Process(target=serve_forever, args=(s,)).start()

s.serve_forever()
