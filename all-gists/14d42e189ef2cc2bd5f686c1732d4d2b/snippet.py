import multiprocessing as mp

class threaded_batch_iter(object):
    '''
    Batch iterator to make transformations on the data. 
    Uses multiprocessing so that batches can be created on CPU while GPU runs previous batch
    '''
    def __init__(self, batchsize):
        self.batchsize = batchsize

    def __call__(self, X, y):
        self.X, self.y = X, y
        return self

    def __iter__(self):
        '''
        multi thread the iter so that the GPU does not have to wait for the CPU to process data
        runs the _gen_batches function in a seperate process so that it can be run while the GPU is running previous batch
        '''
        q = mp.Queue(maxsize=128)

        def _gen_batches():
            num_samples = len(self.X)
            idx = np.random.permutation(num_samples)
            batches = range(0, num_samples - self.batchsize + 1, self.batchsize)
            for batch in batches:
                X_batch = self.X[idx[batch:batch + self.batchsize]]
                y_batch = self.y[idx[batch:batch + self.batchsize]]
          
                # do some stuff to the batches like augment images or load from folders
                
                yield [X_batch, y_batch]

        def _producer(_gen_batches):
            # load the batch generator as a python generator
            batch_gen = _gen_batches()
            # loop over generator and put each batch into the queue
            for data in batch_gen:
                q.put(data, block=True)
            # once the generator gets through all data issue the terminating command and close it
            q.put(None)
            q.close()
        
        # start the producer in a seperate process and set the process as a daemon so it can quit easily if you ctrl-c
        thread = mp.Process(target=_producer, args=[_gen_batches])
        thread.daemon = True
        thread.start()
        
        # grab each successive list containing X_batch and y_batch which were added to the queue by the generator
        for data in iter(q.get, None):
            yield data[0], data[1]

# ==================================================================================================================
# to use it do the following when looping over epochs
batch_iter = threaded_batch_iter(batchsize=128)

for epoch in range(epochs):
    # ...
    for X_batch, y_batch in batch_iter(X_train, y_train):
        # ...