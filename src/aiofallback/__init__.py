import asyncio
from collections.abc import Callable, Sequence
from functools import lru_cache
from importlib import import_module

__version__ = "0.1.0"
__author__ = "Vizonex"

__all__ = ("EventLoopNotFoundError", "clear_import_cache", "get_loop_factory")


class EventLoopNotFoundError(Exception):
    """Raised when modules required are not found"""

    __slots__ = ("modules",)

    def __init__(self, modules: Sequence[str]) -> None:
        self.modules = modules
        super().__init__()

    def __str__(self) -> str:
        loops = ", ".join(map(repr, self.modules))
        return f"provided module{'s' if len(self.modules) > 1 else ''}: {loops} not found"


def _get_factory(
    module: str, factory_name: str = "new_event_loop"
) -> Callable[[], asyncio.AbstractEventLoop] | asyncio.AbstractEventLoop | None:
    try:
        if "." in module:
            name, package = module.rsplit(".", 1)
            getattr(import_module(name, package), factory_name, None)
        return getattr(import_module(module), factory_name, None)
    except (ModuleNotFoundError, ImportError):
        return

# 128 different loops is a little bit too much so will keep the limit at 16.
_cache = lru_cache(16)(_get_factory)


# NOTE: Delimiter logic is inspired by uvicorn.


def get_loop_factory(
    *modules: str,
    on_failed: Callable[[str], None] | None = None,
    on_found: Callable[[str], None] | None = None,
    default_factory: Callable[[], asyncio.AbstractEventLoop]
    | asyncio.AbstractEventLoop
    | None = None,
    use_cache: bool = True,
) -> Callable[[], asyncio.AbstractEventLoop] | asyncio.AbstractEventLoop:
    """Gets the best possible loop factory it can import
    the logic is based on the list given if 'a' is first
    and 'a' is found then 'a' is chosen otherwise if 'b'
    is present pick 'b' and so on and so forth.

    :param modules: names of module to try and import
        if `::` delimiter is not present the attribute
        called will utilize `new_event_loop` as it's
        given attribute to import.

    :param on_failed: logs modules that failed to be imported
    :param on_found: logs the modules that are found.
    :param default_factory: if set it will be the last resort.
    :param use_cache: if `True` use lru-cache when importing each
        attribute. This can greatly speedup performance but
        this can eat more memory.

    :raises EventLoopNotFoundError: when no default_factory
        is set to fall back to when all modules have failed
        to be imported.

    """
    __get_factory = _cache if use_cache else _get_factory
    has_found_cb = on_found is not None
    has_failed_cb = on_failed is not None
    if has_failed_cb and not callable(on_failed):
        raise TypeError("on_failed must be callable")
    if has_found_cb and not callable(on_found):
        raise TypeError("on_found must be callable")

    for mod in modules:
        if "::" in mod:
            module, factory_name = mod.rsplit("::", 1)
            factory = __get_factory(module, factory_name)
        else:
            factory = __get_factory(mod)
        if factory is not None:
            if has_found_cb:
                on_found(mod)
            return factory
        else:
            if has_failed_cb:
                on_failed(mod)

    if default_factory is not None:
        return default_factory

    raise EventLoopNotFoundError(modules)


def clear_import_cache() -> None:
    """resets aiofallback's import cache by clearing it"""
    _cache.cache_clear()
