import random

def coroutine(func):
    """A decorator to automatically prime coroutines"""
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr
    return start

@coroutine
def consumer():
    """Tells us if a number is 2 or not"""
    # Wait here until we get sent something
    while True:
        num = yield
        if num == 2:
            print("The number {} is 2".format(num))
        else:
            print("The number {} is not 2".format(num))

def producer(consumer):
    """Produces random numbers up to 20"""
    while True:
        # Produce a random number and send it to the consumer
        r = random.randint(0, 20)
        consumer.send(r)
        # Wait here until next() is called
        yield

if __name__ == "__main__":
    # Set up generators
    c = consumer()
    p = producer(c)

    # Produce 10 random numbers
    for _ in range(10):
        next(p)
