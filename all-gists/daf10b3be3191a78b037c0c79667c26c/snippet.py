# -*- coding: utf-8 -*-

import asyncio
import uvloop
from aiohttp.web import Application, MsgType, WebSocketResponse


def add_socket(app, socket, user_id):
    if user_id in app['connections']:
        pass
    else:
        print('New connection added {}'.format(user_id))
        app['connections'][user_id] = socket


async def remove_socket(app, socket, user_id):
    app['connections'].pop(user_id, None)
    print('user id: {} is disconnected')
    await socket.close()


async def ws_handler(request):
    ws = WebSocketResponse()
    await ws.prepare(request)
    user_id = request.GET.get('user_id', -1)

    async for msg in ws:
        if msg.tp == MsgType.text:
            if msg.data == 'close':
                await remove_socket(app=ws.app, socket=ws, user_id=user_id)
            else:
                add_socket(app=request.app, socket=ws, user_id=user_id)
                ws.send_str(msg.data * 2)
    return ws

async def init(loop):
    app = Application(loop=loop)
    app['connections'] = {}
    app.router.add_route('GET', '/', ws_handler)

    handler = app.make_handler()
    srv = await loop.create_server(handler, '127.0.0.1', '8000')
    print("Server running on 127.0.0.1:8000")
    return app, srv, handler


async def cleanup(app, srv, handler):
    for idx, ws in app['connections'].items():
        ws.close()
    await asyncio.sleep(0.1)
    srv.close()
    await handler.finish_connections()
    await srv.wait_closed()


def main():
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    app, srv, handler = loop.run_until_complete(init(loop))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(cleanup(app, srv, handler))


if __name__ == "__main__":
    main()
