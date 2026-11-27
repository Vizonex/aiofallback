# Aiofallback
An event loop fallback system for asyncio for handpicking the best event-loop module
based on your perferred import order. This has the same features as uvicorn when it comes to 
importing what is needed otherwise `new_event_loop` will be the assumed default.
It has no extra dependencies with only 2 functions one to clear an import cache and the 
other to get the eventloops desired.

```python
from asyncio import Runner, get_running_loop, new_event_loop

from aiofallback import get_loop_factory


async def main():
    loop = get_running_loop()
    # <uvloop.Loop running=True closed=False debug=False>
    # <rsloop.Loop running=True closed=False debug=False>
    print(loop)


if __name__ == "__main__":
    with Runner(
        loop_factory=get_loop_factory(
            "uvloop", "rsloop::Loop", "blazio", default_factory=new_event_loop
        )
    ) as runner:
        runner.run(main())
```

