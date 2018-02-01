def reusable(generator):
    """Convert a generator into a ReusableIterator."""
    
    class ReusableIterator:
        """Create an wrapper for a generator to allow repeated iteration."""

        def __init__(self, *args, **kwargs):
            """Store the arguments to pass to the wrapped generator."""
            self.args = args
            self.kwargs = kwargs

        def __iter__(self):
            """Return an iterator that yields values from the generator."""
            yield from generator(*self.args, **self.kwargs)

    return ReusableIterator