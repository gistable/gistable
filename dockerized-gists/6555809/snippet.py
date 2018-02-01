import contextlib
import linecache
import logging
import sys
import traceback
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO


class PurgingDictionary(dict):
    """Special dictionary that can be purged.

    Calling purge() removes the keys that have not been requested since the
    last call to purge().
    This is useful to remove keys that are not needed anymore, when the keys
    cannot be weakly referenced.
    """
    def __init__(self):
        dict.__init__(self)
        self.__seen_keys = set()

    def __mark_seen(self, key):
        while key is not None:
            if key in self.__seen_keys:
                break
            self.__seen_keys.add(key)
            key = key.f_back

    def __getitem__(self, key):
        self.__mark_seen(key)
        return dict.__getitem__(self, key)

    def get(self, key, default=None):
        self.__mark_seen(key)
        return dict.get(self, key, default)

    def setdefault(self, key, default=None):
        self.__mark_seen(key)
        return dict.setdefault(self, key, default)

    def purge(self):
        """Removes entries that have not been queried since the last call.
        """
        if not self.__seen_keys:
            self.clear()
            self.__seen_keys = set()
            return

        for k in self.keys():
            if k not in self.__seen_keys:
                del self[k]
        self.__seen_keys = set()


# Gets the current frame (from logging)
def currentframe():
    try:
        raise Exception
    except:
        return sys.exc_info()[2].tb_frame.f_back
if hasattr(sys, '_getframe'): currentframe = lambda: sys._getframe(3)


class DefaultContext(object):
    """Default context formatter.
    """
    def __init__(self, msg=None, **kwargs):
        self.msg = msg
        self.kwargs = kwargs

    def __str__(self):
        if self.kwargs:
            kw = ', '.join('%s=%r' % (k, v)
                           for k, v in self.kwargs.iteritems())
            if self.msg:
                return "%s (%s)" % (self.msg, kw)
            else:
                return "(%s)" % kw
        elif self.msg:
            return self.msg


_context_class = DefaultContext


def set_context_class(cls):
    """Changes the class used to build/format contexts.

    This class gets passed the arguments that were given to push() or pushed(),
    and is converted to a string to be put in the traceback.
    """
    global _context_class
    _context_class = cls


pushed_infos = PurgingDictionary()


class Formatter(logging.Formatter):
    """Logging formatter that inserts the context objects in the traceback.
    """
    def formatException(self, ei):
        etype, value, tb = ei[:3]
        formatted = []
        formatted.append("Traceback (most recent call last):")
        while tb is not None:
            f = tb.tb_frame
            lineno = tb.tb_lineno
            co = f.f_code
            filename = co.co_filename
            name = co.co_name
            item = '  File "%s", line %d, in %s' % (filename, lineno, name)

            frame_contexts = pushed_infos.get(f)
            if frame_contexts:
                for ctx in frame_contexts:
                    item += '\n  %s' % ctx

            linecache.checkcache(filename)
            line = linecache.getline(filename, lineno, f.f_globals)
            if line:
                item += '\n    ' + line.strip()

            formatted.append(item)
            tb = tb.tb_next
        formatted.append("%s: %s" % (etype.__name__, value.message))
        return '\n'.join(formatted)


def push(*args, **kwargs):
    """Push some context onto the stack.

    You don't have to pop this, it is associated with the caller's stack frame.
    """
    f = currentframe().f_back
    frame_contexts = pushed_infos.setdefault(f, [])
    frame_contexts.append(_context_class(*args, **kwargs))


@contextlib.contextmanager
def pushed(*args, **kwargs):
    """Push some context onto the stack.

    The context is removed when leaving the context manager.
    """
    frame_contexts = pushed_infos.setdefault(currentframe().f_back, [])
    ctx = _context_class(*args, **kwargs)
    idx = len(frame_contexts)
    frame_contexts.append(ctx)
    try:
        yield
    finally:
        del frame_contexts[idx]
