import asyncio
from typing import Any, Awaitable, Callable, Optional, Type

# eh, like the @cached_property idiom, but async and you do `await x.y`


class async_cached_property:
    name: str

    def __init__(self, getter: Callable[[], Awaitable]) -> None:
        self._getter = getter
        self.name = self._getter.__name__

    def __get__(self, instance: Optional[Any], cls: Type) -> Awaitable:
        if instance is None:
            return self
        try:
            followers_future = instance.__dict__[self.name]
            return followers_future
        except KeyError:
            followers_future = instance.__dict__[self.name] = asyncio.Future()
            winners_future = asyncio.ensure_future(self._getter(instance))
            winners_future.add_done_callback(
                lambda fut: followers_future.set_result(fut.result()))
            return winners_future


class X:

    @async_cached_property
    async def y(self) -> float:
        await asyncio.sleep(1.0)
        return 1.0


async def test():
    x = X()
    print(await x.y)
    for i in range(100):
        print(await x.y)


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
