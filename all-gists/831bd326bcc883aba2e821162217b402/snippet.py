import asyncio


class FunctionPool:
    '''Connection pool の関数版みたいなやつ考える

    * 同時に使っていい分だけ関数が pool されている
    * 関数を使いたいときはそこから1個取り出して使う
    * 使い終わったら pool に戻す
    * pool が空なら誰かが使い終わって戻してくれるまで待つ
    '''
    def __init__(self, functions):
        self._queue = asyncio.Queue()

        for f in functions:
            self._queue.put_nowait(f)

    def use(self):
        # XXX: "use" は微妙なので何かいい名前ないか
        return PooledFunction(self)

    def get(self):
        return self._queue.get()

    def put(self, value):
        return self._queue.put(value)


# XXX: "PooledFunction" というの微妙に意味合ってない気が...
class PooledFunction:
    def __init__(self, pool):
        self._pool = pool
        self._function = None

    async def __aenter__(self):
        self._function = await self._pool.get()

        return self._function

    async def __aexit__(self, exc_type, exc, tb):
        assert self._function is not None

        await self._pool.put(self._function)


def _test():
    import time

    async def func():
        await asyncio.sleep(1)
        print('hi')

    pool = FunctionPool([func, func])

    async def worker(wid):
        print(int(time.time()), 'begin worker:', wid)

        async with pool.use() as f:
            await f()

        print(int(time.time()), 'end worker:', wid)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait([worker(i) for i in range(5)]))


if __name__ == '__main__':
    _test()
