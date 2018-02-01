# This demo is a transliteration of the below referenced demo to use the async/await syntax
#
#https://www.reddit.com/r/Python/comments/33ecpl/neat_discovery_how_to_combine_asyncio_and_tkinter/

#
# For testing purposes you may use the following command to create a test daemon:
# tail -f /var/log/messages | nc -l 5900
# Enter localhost:5900 in the entry box to connect to it.

from tkinter import *
import asyncio

async def run_tk(root, interval=0.05):
    '''
    Run a tkinter app in an asyncio event loop.
    '''
    try:
        while True:
            root.update()
            await asyncio.sleep(interval)
    except TclError as e:
        if "application has been destroyed" not in e.args[0]:
            raise

async def tclient(addr,port):
    print('tclient',addr,port)
    try:
        sock ,_= await asyncio.open_connection(host=addr,port=port)
       #print(sock)
       #f=sock.as_stream()
        while True:
               #data = yield from f.readline() 
                data = await sock.readline()
                if not data:break
                data=data.decode()
                print(data,end='\n' if data[-1]=='\r' else'')
    except:
        pass


async def main():
    root = Tk()
    entry = Entry(root)
    entry.grid()
    
    def spawn_ws_listener():
       addr=entry.get().split(':')
       print('spawn',addr)
       return asyncio.ensure_future( tclient( addr[0],int(addr[1]) ) )

    Button(root, text='Connect', command=spawn_ws_listener).grid()
    
    await run_tk(root)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())