# coding=utf-8
"""
Demonstrates how a [Mapped Diagnostic Context](http://logback.qos.ch/manual/mdc.html)
of log4j MDC fame (and also provided in slf4j) could be implemented in Python
"""
import json
import logging
import sys
import threading

# this has to be a global variable:
# http://stackoverflow.com/questions/1408171/thread-local-storage-in-python
logging._mdc = threading.local()


def set_mdc(key, value):
    """
    :type key: str or unicode
    :type value: object
    """
    setattr(logging._mdc, key, value)
logging.set_mdc = set_mdc
del set_mdc


def get_mdc():
    """
    :rtype: dict from str to object
    """
    results = {}
    for x in dir(logging._mdc):
        if x.startswith('__'):
            continue
        results[x] = getattr(logging._mdc, x)
    return results
logging.get_mdc = get_mdc
del get_mdc


def clear_mdc():
    for k in logging.get_mdc():
        delattr(logging._mdc, k)
logging.clear_mdc = clear_mdc
del clear_mdc


def with_mdc(**kw_args):
    def decorate(f):
        for k in kw_args:
            v = kw_args[k]
            logging.set_mdc(k, v)

        def wrapped_f(*args, **kw):
            try:
                return f(*args, **kw)
            finally:
                logging.clear_mdc()
        return wrapped_f
    return decorate
logging.with_mdc = with_mdc
del with_mdc


class MDCFormatter(logging.Formatter):

    def format(self, record):
        parts = {}
        for k, v in logging.get_mdc().items():
            p_name = 'MDC:%s' % k
            parts[p_name] = v
            del p_name
        for x in dir(record):
            if x.startswith('__'):
                continue
            it = getattr(record, x)
            if isinstance(it, str) or isinstance(it, unicode):
                parts[x] = it
            elif 'getMessage' == x:
                parts[x] = record.getMessage()
            else:
                parts[x] = repr(it)
            del it
        result = json.dumps(parts)
        del parts
        # print('format <= %r' % result)
        return result

    def formatException(self, ei):
        result = 'MDC(%r) EXCEPTION=%r' % (logging.get_mdc(), ei)
        # print('formatException <= %r' % result)
        return result

hand = logging.StreamHandler(stream=sys.stderr)
hand.setFormatter(MDCFormatter())
logging.root.addHandler(hand)
del hand
logging.root.setLevel(logging.DEBUG)

LOGGER = logging.getLogger('a.b.c')


@logging.with_mdc(a='called from a')
def a(body, meta):
    print('the body of %r is %r' % (meta['url'], body))
    print('a.1')
    b()
    print('a.2')


def b():
    print('b.1')
    LOGGER.info('Hello from b')
    try:
        x = json.loads('{')
    except ValueError:
        LOGGER.exception('Unable to parse the text')
    print('b.2')

if __name__ == '__main__':
    a('<html></html>', {'url': 'http://localhost'})
    LOGGER.info('Bye, now')
