
class Func(object):

    _on_start = list()
    _on_exit = list()

    @classmethod
    def register_on_start(cls, callback):
        cls._on_start.append(callback)

    @classmethod
    def register_on_exit(self, callback):
        self._on_exit.append(callback)

    def run(self):
        self._run_callbacks(self._on_start)
        self._run_callbacks(self._on_exit)

    def _run_callbacks(self, callbacks):
        for callback in callbacks:
            callback(self)


_proc_data = dict()


def _on_start(proc):
    proc_data = id(proc)
    _proc_data[proc] = proc_data


def _on_exit(proc):
    proc_data = _proc_data.pop(proc)
    print 'on_exit', proc_data


def main():
    Func.register_on_start(_on_start)
    Func.register_on_exit(_on_exit)
    f = Func()
    f.run()


if __name__ == '__main__':
    main()
