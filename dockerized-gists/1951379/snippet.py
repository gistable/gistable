def coroutine(func):
    """
    A decorator that turns a function with normal input into a coroutine.
    This decorator takes care of priming the coroutine, doing the looping and
    handling the closing.
    
    The first argument of any decorated function is what was received when 
    data was sent to the coroutine via the ``.send`` method. All the other
    ``*args`` and ``**kwargs`` are what was passed to the decorated function
    when instantiating the coroutine.
    
    Using named arguments is recommended for less confusion.
    
    ::
    
        @coroutine
        def tailgrep(input = None, pattern = None):
            if pattern in input:
                print input
        
        t = tailgrep(pattern = 'Python')
        
        for line in lines:
            t.send(line)
        
    """
    def routine(*args, **kwargs):
        try:
            while True:
                input = (yield)
                func(input = input, *args, **kwargs)
        except StopIteration:
            pass
    def start(*args, **kwargs):
        coroutine = routine(*args, **kwargs)
        coroutine.next()
        return coroutine
    return start