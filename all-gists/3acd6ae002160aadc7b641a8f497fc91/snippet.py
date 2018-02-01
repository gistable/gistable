import asyncio
import random

async def slow_action():
    await asyncio.sleep(random.randrange(1, 5))


async def my_range(n):
    i = 0
    while i < n:
        await slow_action()
        yield i
        i += 1


async def example(task_id, n):
    async for i in my_range(n):
        print(f'[{task_id}] async for {i}')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(example(i, 10)) for i in range(4)]
    try:
        app = loop.run_until_complete(
            asyncio.wait(tasks)
        )
    finally:
        loop.close()