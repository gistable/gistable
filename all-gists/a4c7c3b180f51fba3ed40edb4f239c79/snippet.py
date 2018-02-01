import rethinkdb as r
import asyncio

r.set_loop_type("asyncio")

async def get_connection():
    return await r.connect("localhost", 28015)

async def changefeed_old():

    conn = await get_connection()
    changes = await r.db("test").table("test").changes()["new_val"].run(conn)

    async for change in changes:
        print(change)

async def changefeed_new():
    conn = await get_connection()
    changes = await r.db("test").table("test").changes()["old_val"].run(conn)

    async for change in changes:
        print(change)

loop = asyncio.get_event_loop()
loop.create_task(changefeed_old())
loop.create_task(changefeed_new())
loop.run_forever()