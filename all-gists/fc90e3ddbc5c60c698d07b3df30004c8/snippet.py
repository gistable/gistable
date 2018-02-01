import asyncio
from aiohttp import web
import subprocess


async def uptime_handler(request):
    # http://HOST:PORT/?interval=90
    interval = int(request.GET.get('interval', 1))
    
    # Without the Content-Type, most (all?) browsers will not render 
    # partially downloaded content. Note, the response type is 
    # StreamResponse not Response.
    resp = web.StreamResponse(status=200, 
                              reason='OK', 
                              headers={'Content-Type': 'text/html'})
    
    # The StreamResponse is a FSM. Enter it with a call to prepare.
    await resp.prepare(request)
    
   
    
    while True:
        try:
            # Technically, subprocess blocks, so this is a dumb call 
            # to put in an async example. But, it's a tiny block and 
            # still mocks instantaneous for this example.
            resp.write(b"<strong>")
            resp.write(subprocess.check_output('uptime'))
            resp.write(b"</strong><br>\n")
            
            # Yield to the scheduler so other processes do stuff.
            await resp.drain()
            
            # This also yields to the scheduler, but your server 
            # probably won't do something like this. 
            await asyncio.sleep(interval)
        except Exception as e:
            # So you can observe on disconnects and such.
            print(repr(e))
            raise
    
    return resp


async def build_server(loop, address, port):
    # For most applications -- those with one event loop -- 
    # you don't need to pass around a loop object. At anytime, 
    # you can retrieve it with a call to asyncio.get_event_loop(). 
    # Internally, aiohttp uses this pattern a lot. But, sometimes 
    # "explicit is better than implicit." (At other times, it's 
    # noise.) 
    app = web.Application(loop=loop)
    app.router.add_route('GET', "/uptime", uptime_handler)
    
    return await loop.create_server(app.make_handler(), address, port)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(build_server(loop, 'localhost', 9999))
    print("Server ready!")
    
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Shutting Down!")
        loop.close()