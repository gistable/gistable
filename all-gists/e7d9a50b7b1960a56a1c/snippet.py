from tkinter import *
import asyncio
from functools import wraps
import websockets

def runloop(func):
    '''
    This decorator converts a coroutine into a function which, when called,
    runs the underlying coroutine to completion in the asyncio event loop.
    '''
    func = asyncio.coroutine(func)
    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(func(*args, **kwargs))
    return wrapper

@asyncio.coroutine
def run_tk(root, interval=0.05):
    '''
    Run a tkinter app in an asyncio event loop.
    '''
    try:
        while True:
            root.update()
            yield from asyncio.sleep(interval)
    except TclError as e:
        if "application has been destroyed" not in e.args[0]:
            raise

@asyncio.coroutine
def listen_websocket(url):
    '''
    Connect to a websocket url, then print messages received on the connection
    until closed by the server.
    '''
    ws = yield from websockets.connect(url)
    while True:
        msg = yield from ws.recv()
        if msg is None:
            break
        print(msg)

@runloop
def main():
    root = Tk()
    entry = Entry(root)
    entry.grid()
    
    def spawn_ws_listener():
        return asyncio.async(listen_websocket(entry.get()))

    Button(root, text='Print', command=spawn_ws_listener).grid()
    
    yield from run_tk(root)

if __name__ == "__main__":
    main()