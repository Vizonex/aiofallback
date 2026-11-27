from asyncio import SelectorEventLoop


class LoopB(SelectorEventLoop):
    pass


def new_event_loop() -> LoopB:
    return LoopB()
