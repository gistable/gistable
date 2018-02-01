
import multiprocessing
import os
import threading
import time


def child_thread(lock):
    with lock:
        time.sleep(10)

    print('work done.')


def child_worker(lock):
    print('run child worker..')
    with lock:
        print('got lock...')

    print('child worker exit.')


def run_fork():
    lock = threading.Lock()
    child_t = threading.Thread(target=child_thread, args=(lock,))
    child_t.start()
    time.sleep(3)
    print('main thread identity in parent process', threading.get_ident())
    pid = os.fork()
    if pid == -1:
        raise RuntimeError('fork failed.')

    if pid == 0:
        print('main thread identity in child process', threading.get_ident())
        child_worker(lock)
    else:
        time.sleep(3600)

def main():
    run_fork()


if __name__ == '__main__':
    main()
