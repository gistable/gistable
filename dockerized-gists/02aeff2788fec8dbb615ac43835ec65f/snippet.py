import time, threading
def delay(func, timeout):
    time.sleep(timeout)
    func()


def settimeout(func, timeout):
    thread = threading.Thread(target=delay, args=(func, timeout))
    thread.start()
    return thread
