def distribute(through, proceed):
    def wrapper(f):
        def wrapped(*args, **kwargs):

            all_launched = False
            results = []

            def callback():
                #print 'Worker is done. Intermediate results: %s' % results
                if all_launched and all(results):
                    proceed([res[0] for res in results])

            def launch(args):
                import threading

                class TaskThread(threading.Thread):
                    def __init__(self, *args, **kwargs):
                        self.callback = kwargs.pop('callback')
                        super(TaskThread, self).__init__(*args, **kwargs)

                    def run(self):
                        super(TaskThread, self).run()
                        self.callback()

                index, task = args
                results.append(None)
                thread = TaskThread(target=through, args=[task],
                                    kwargs={'results': results, 'index': index},
                                    callback=callback)
                thread.start()

            map(launch, enumerate(f(*args, **kwargs)))
            all_launched = True
            #print 'All [%d] tasks launched' % len(results)

        return wrapped

    return wrapper


def worker(f):
    def wrapped(*args, **kwargs):
        results = kwargs.pop('results')
        index = kwargs.pop('index')
        results[index] = [f(*args, **kwargs)]
    return wrapped


@worker
def handler(task):
    import time
    time.sleep(task['delay'])
    return task['index'] ** 2


def consumer(results):
    print 'Results: %s' % results


@distribute(through=handler, proceed=consumer)
def producer(tasks_count):
    import random, time
    for i in xrange(tasks_count):
        time.sleep(random.randint(0, 2))
        print 'Handling task #%d' % i
        yield {'index': i,
               'delay': random.randint(1, 10)}

if __name__ == '__main__':
    producer(5)
