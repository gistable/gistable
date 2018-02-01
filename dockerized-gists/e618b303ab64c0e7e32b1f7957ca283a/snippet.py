from types import TracebackType
from typing import (Any, Callable, Iterable, Mapping,
                    Optional, Sequence, Tuple, Union)

__all__ = ('Environ', 'ExcInfo', 'StartResponseCallable',
           'StartResponseCallableWithExcInfo', 'WriteCallable',
           'WsgiApplication')


# https://www.python.org/dev/peps/pep-3333/#the-write-callable
WriteCallable = Callable[[bytes], Any]

# https://docs.python.org/3/library/sys.html#sys.exc_info
ExcInfo = Tuple[type, BaseException, TracebackType]

# https://www.python.org/dev/peps/pep-3333/#the-start-response-callable
StartResponseCallable = Callable[
    [
        str,  # status
        Sequence[Tuple[str, str]],  # response headers
    ],
    WriteCallable  # write() callable
]
StartResponseCallableWithExcInfo = Callable[
    [
        str,  # status
        Sequence[Tuple[str, str]],  # response headers
        Optional[ExcInfo]  # exc_info
    ],
    WriteCallable  # write() callable
]

# https://www.python.org/dev/peps/pep-3333/#environ-variables
Environ = Mapping[str, object]

# https://www.python.org/dev/peps/pep-3333/#specification-details
WsgiApplication = Callable[
    [
        Environ,  # environ
        Union[
            StartResponseCallable,
            StartResponseCallableWithExcInfo
        ],  # start_response() function
    ],
    Iterable[bytes]  # bytestring chunks
]