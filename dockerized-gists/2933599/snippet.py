from kombu import Exchange
from kombu import Queue
from kombu import BrokerConnection

class ProduceConsume(object):
    def __init__(self, exchange_name, **options):
        exchange = Exchange(exchange_name, type='fanout', durable=False)
        queue_name = options.get('queue', exchange_name+'_queue')
        self.queue = Queue(queue_name ,exchange)

    def producer(self):
        def make():
            with BrokerConnection('localhost') as conn:
                with conn.SimpleQueue(self.queue) as queue:
                    while True:
                        payload = (yield)
                        queue.put(payload)
        producer = make()
        producer.next()
        return producer

    def consumer(self):
        with BrokerConnection('localhost') as conn:
            with conn.SimpleQueue(self.queue) as queue:
                while True:
                    message = queue.get()
                    message.ack()
                    yield message.payload
                    message = queue.get()
                    message.ack()
    @classmethod
    def test(cls, *args):
        import time
        exchange = 'MaMouMo-Test'
        if args[0] =='produce':
            producer = ProduceConsume(exchange).producer()
            for i in range(10000):
                producer.send(dict(count=i))
        if args[0] =='consume':
            for message in ProduceConsume(exchange, queue=args[1]).consumer():
                print message




if __name__ =='__main__':
    """
    to run the producer 
    $ python kombu_example.py produce 

    to run the comsumer
    $ python kombu_example.py consume my_queue
    
    """
    import sys
    ProduceConsume.test(*sys.argv[1:])
