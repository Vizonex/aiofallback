import asyncio

import pytest

from aiofallback import get_loop_factory, EventLoopNotFoundError


@pytest.mark.parametrize(
    argnames=("modules", "found_result", "failed_result"),
    argvalues=(
        (("modules.a", "modules.b", "modules.c"), "modules.b", ["modules.a"]),
        (("modules.a::LoopA", "modules.b", "modules.c"), "modules.a::LoopA", []),
        (("modules.b::new_event_loop", "modules.c"), "modules.b::new_event_loop", []),
        (
            ("nonexistant", "modules.b::new_event_loop", "modules.c"),
            "modules.b::new_event_loop",
            ["nonexistant"],
        ),
        (("modules.b::LoopB", "modules.c::LoopC"), "modules.b::LoopB", []),
        (("modules.c::LoopC",), "modules.c::LoopC", []),
        (("modules.c::new_event_loop",), "modules.c::new_event_loop", []),
    ),
)
def test_event_loop_imports(
    modules: tuple[str, ...], found_result: str, failed_result: list[str]
) -> None:
    found = []
    failed = []

    factory = get_loop_factory(*modules, on_found=found.append, on_failed=failed.append)

    assert isinstance(factory, asyncio.AbstractEventLoop) or callable(factory)

    assert found_result == found[0]
    assert failed == failed_result


def test_failure() -> None:

    with pytest.raises(EventLoopNotFoundError, match=r"provided module: 'non_existant' not found"):
        get_loop_factory("non_existant")

    with pytest.raises(EventLoopNotFoundError, match=r"provided modules: 'non_existanta', 'non_extistantb' not found"):
        get_loop_factory("non_existanta", "non_extistantb")


def test_default() -> None:
    from modules.a import LoopA

    factory = get_loop_factory("non_existanta", "non_existantb", default_factory=LoopA)
    assert factory is LoopA




    