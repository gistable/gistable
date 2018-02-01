from __future__ import print_function

import gc
import threading
import time
import unittest
import weakref

from functools import partial


class ThreadWatcher(object):
    class Vigil(object):
        pass

    def __init__(self):
        self._refs = {}
        self._local = threading.local()

    def _on_death(self, vigil_id, callback, ref):
        self._refs.pop(vigil_id)
        callback()

    def watch(self, callback):
        if not self.is_watching():
            self._local.vigil = v = ThreadWatcher.Vigil()
            on_death = partial(
                self._on_death, id(v), callback)

            ref = weakref.ref(v, on_death)
            self._refs[id(v)] = ref

    def is_watching(self):
        "Is the current thread being watched?"
        try:
            v = self._local.vigil
            return id(v) in self._refs
        except AttributeError:
            return False

    def unwatch(self):
        try:
            v = self._local.vigil
            del self._local.vigil
            self._refs.pop(id(v))
        except AttributeError:
            pass


try:
    # Python 2
    import thread

    def get_ident():
        return thread.get_ident()

except ImportError:
    # Python 3
    def get_ident():
        return threading.get_ident()


class TestWatch(unittest.TestCase):
    def test_watch(self):
        print('main', get_ident())
        watcher = ThreadWatcher()
        callback_ran = [False]

        def callback():
            print('callback', get_ident())
            callback_ran[0] = True

        def target():
            watcher.watch(callback)

        t = threading.Thread(target=target)
        t.start()
        t.join()
        # Trigger collection in Py 2.6, see http://bugs.python.org/issue1868
        watcher.is_watching()
        gc.collect()
        for _ in range(10):
            if callback_ran[0]:
                break
            else:
                time.sleep(.1)
        assert callback_ran[0]
        # id(v) removed from _refs
        assert not watcher._refs

    def test_unwatch(self):
        watcher = ThreadWatcher()
        callback_ran = [False]

        def callback():
            callback_ran[0] = True

        def target():
            watcher.watch(callback)
            watcher.unwatch()

        t = threading.Thread(target=target)
        t.start()
        t.join()
        # Trigger collection in Py 2.6, see http://bugs.python.org/issue1868
        watcher.is_watching()
        gc.collect()
        assert not callback_ran[0]

    def test_unwatch_twice(self):
        watcher = ThreadWatcher()
        assert not watcher.is_watching()
        watcher.unwatch()
        assert not watcher.is_watching()
        watcher.watch(lambda _: None)
        assert watcher.is_watching()
        watcher.unwatch()
        assert not watcher.is_watching()
        watcher.unwatch()
        assert not watcher.is_watching()


class TestRefLeak(unittest.TestCase):
    def test_leak(self):
        watcher = ThreadWatcher()
        n_callbacks = [0]
        nthreads = 10

        def callback():
            # BAD, NO!:
            # Accessing thread-local in callback
            watcher.is_watching()
            n_callbacks[0] += 1

        def target():
            watcher.watch(callback)

        for _ in range(nthreads):
            t = threading.Thread(target=target)
            t.start()
            t.join()

        watcher.is_watching()
        gc.collect()
        for _ in range(10):
            if n_callbacks[0] == nthreads:
                break
            else:
                time.sleep(.1)

        self.assertEqual(nthreads, n_callbacks[0])


if __name__ == '__main__':
    unittest.main()
