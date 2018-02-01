"""Utilities for managing database sessions."""
from __future__ import with_statement

import contextlib
import functools

@contextlib.contextmanager
def temp_session(session_cls, **kwargs):
    """Quick and dirty context manager that provides a temporary Session object
       to the nested block. The session is always closed at the end of the block.
       
       This is useful if only SELECTs and the like are being done; anything involving
       INSERTs, UPDATEs etc should use transactional_session."""
    session = session_cls(**kwargs)
    yield session

@contextlib.contextmanager
def transactional_session(session_cls, nested=True, **kwargs):
    """Context manager which provides transaction management for the nested
       block. A transaction is started when the block is entered, and then either
       committed if the block exits without incident, or rolled back if an error
       is raised.
       
       Nested (SAVEPOINT) transactions are enabled by default, unless nested=False is
       passed, meaning that this context manager can be nested within another and the
       transactions treated as independent units-of-work from the perspective of the nested
       blocks. If the error is handled further up the chain, the outer transactions will
       still be committed, while the inner ones will be rolled-back independently."""
    session = session_cls(**kwargs)
    session.begin(nested=nested)
    try:
        yield session
    except:
        # Roll back if the nested block raised an error
        session.rollback()
        raise
    else:
        # Commit if it didn't (so flow ran off the end of the try block)
        session.commit()

def in_transaction(**session_kwargs):
    """Decorator which wraps the decorated function in a transactional session. If the
       function completes successfully, the transaction is committed. If not, the transaction
       is rolled back."""
    def outer_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with transactional_session(**session_kwargs):
                return func(*args, **kwargs)
        return wrapper
    return outer_wrapper
