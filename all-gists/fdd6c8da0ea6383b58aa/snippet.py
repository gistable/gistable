
import asyncio
import websockets
from websockets.exceptions import ConnectionClosed
from jsonrpc import JSONRPCResponseManager, dispatcher


@dispatcher.add_method
def hello(*params):
    return 'hello'+repr(params)


async def app(ws, path):
    while True:
        try:
            message = await ws.recv()
            response = JSONRPCResponseManager.handle(message, dispatcher)
            if response is not None:
                await ws.send(response.json)
        except ConnectionClosed:
            pass


address = '0.0.0.0'
port = 8888

if __name__ == '__main__':
    start_server = websockets.serve(app, address, port)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
