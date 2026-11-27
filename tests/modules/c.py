from asyncio import SelectorEventLoop


class LoopC(SelectorEventLoop):
    pass


def new_event_loop() -> LoopC:
    return LoopC()
