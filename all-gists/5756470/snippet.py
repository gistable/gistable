from __future__ import print_function
from tornado.gen import Task, Return, coroutine
import tornado.process
from tornado.ioloop import IOLoop
import subprocess
import time


STREAM = tornado.process.Subprocess.STREAM


@coroutine
def call_subprocess(cmd, stdin_data=None, stdin_async=False):
    """
    Wrapper around subprocess call using Tornado's Subprocess class.
    """
    stdin = STREAM if stdin_async else subprocess.PIPE

    sub_process = tornado.process.Subprocess(
        cmd, stdin=stdin, stdout=STREAM, stderr=STREAM
    )

    if stdin_data:
        if stdin_async:
            yield Task(sub_process.stdin.write, stdin_data)
        else:
            sub_process.stdin.write(stdin_data)

    if stdin_async or stdin_data:
        sub_process.stdin.close()

    result, error = yield [
        Task(sub_process.stdout.read_until_close),
        Task(sub_process.stderr.read_until_close)
    ]

    raise Return((result, error))


def on_timeout():
    print("timeout")
    IOLoop.instance().stop()


@coroutine
def main():

    seconds_to_wait = 3
    deadline = time.time() + seconds_to_wait

    # don't wait too long
    IOLoop.instance().add_timeout(deadline, on_timeout)

    # try to get output using synchronous PIPE for stdin
    result, error = yield call_subprocess('wc', stdin_data="123")
    print('stdin sync: ', result, error)

    # try to get output using asynchronous STREAM for stdin
    result, error = yield call_subprocess('wc', stdin_data="123", stdin_async=True)
    print('stdin async: ', result, error)

    IOLoop.instance().stop()


if __name__ == "__main__":
    ioloop = IOLoop.instance()
    ioloop.add_callback(main)
    ioloop.start()