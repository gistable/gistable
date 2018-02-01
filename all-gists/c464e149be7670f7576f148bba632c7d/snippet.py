from sanic import Sanic
import json
import asyncio


app = Sanic(__name__)
feeds = {}


class Feed(object):
    def __init__(self, app, feed_name):
        self.name = feed_name
        self.app = app
        self.clients = set()

    def __len__(self):
        return len(self.clients)

    async def run(self, client):
        await self._subscribe(client)
        tasks = self.get_tasks(client)
        await asyncio.wait(tasks)

    def get_tasks(self, client):
        consumer_task = asyncio.ensure_future(self._consumer_handler(client))
        producer_task = asyncio.ensure_future(self._producer_handler())

        return [consumer_task, producer_task]

    async def _consumer_handler(self, client):
        while True:
            message = await client.recv()
            print('message arrived', message)
            await self.app.redis.publish(self.name, message)

    async def _producer_handler(self):
        print('producer_handler')
        while True:
            message = await self.app.pubsub.get_message()
            if message:
                print('publishing:', message)
                for client in self.clients:
                    await client.send(json.dumps(message))
            await asyncio.sleep(1)

    async def _subscribe(self, client):
        await self.app.pubsub.subscribe(self.name)
        self.clients.add(client)


def get_feed(feed_name, app):
    if feed_name in feeds:
        return feeds.get(feed_name)
    else:
        feed = Feed(app=app, feed_name=feed_name)
        feeds[feed_name] = feed
        return feed


@app.websocket('/feed/<feed_name>')
async def feed(request, ws, channel_name):
    print(f'The channel_name: {channel_name}')

    feed = get_feed(channel_name, request.app)
    await feed.run(ws)
       
app.run(host="127.0.0.1", port=8000, debug=True)