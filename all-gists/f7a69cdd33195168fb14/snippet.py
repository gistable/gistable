from tornado import gen, ioloop
from rx import Observable




def create_observable(observer):
    observer.on_next(50)
    observer.on_next(2)
    observer.on_next(8)
    observer.on_next(40)

# @gen.coroutine
def do_work(x):
    print("ASYNC %s" % x)

source = (Observable.create(create_observable)
    .delay(1000)
    .map(lambda x: x * 2))

def main():
    print(1)
    source.subscribe(do_work)
    print(2)

if __name__ == '__main__':
    main()
    ioloop.IOLoop.current().start()