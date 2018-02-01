def fibonacci():
    """ Generator yielding Fibonacci numbers
    
    :returns: int -- Fibonacci number as an integer
    """
    x, y = 0, 1
    while True:
        yield x
        x, y = y, x + y
