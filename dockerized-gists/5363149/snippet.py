from __future__ import print_function
from tornado.gen import Task, Return, coroutine
import tornado.process
import subprocess
from tornado.ioloop import IOLoop


STREAM = tornado.process.Subprocess.STREAM


@coroutine
def call_subprocess(cmd, stdin_data=None):
    """
    Wrapper around subprocess call using Tornado's Subprocess class.
    """
    try:
        sprocess = tornado.process.Subprocess(
            cmd,
            stdin=subprocess.PIPE,
            stdout=STREAM,
            stderr=STREAM
        )
    except OSError as e:
        raise Return((None, e))

    if stdin_data:
        sprocess.stdin.write(stdin_data)
        sprocess.stdin.flush()
        sprocess.stdin.close()

    result, error = yield [
        Task(sprocess.stdout.read_until_close),
        Task(sprocess.stderr.read_until_close)
    ]

    raise Return((result, error))


@coroutine
def ls():
    result, error = yield Task(call_subprocess, 'ls')
    raise Return((result, error))


@coroutine
def main():
    result, error = yield ls()
    print(result, error)
    IOLoop.instance().stop()


if __name__ == "__main__":
    ioloop = IOLoop.instance()
    ioloop.add_callback(main)
    ioloop.start()