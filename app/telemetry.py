"""Context-scoped engine telemetry for the Hackathon Judge Trace console."""

import asyncio
from contextvars import ContextVar
from typing import Any, Optional

_sink: ContextVar[Optional[Any]] = ContextVar("cineclear_telemetry_sink", default=None)


def set_telemetry_sink(sink) -> Any:
    return _sink.set(sink)


def reset_telemetry_sink(token) -> None:
    _sink.reset(token)


async def emit_engine_log(source: str, message: str, **extra) -> None:
    sink = _sink.get()
    if not sink:
        return
    payload = {"type": "log", "source": source, "message": message}
    payload.update(extra)
    result = sink(payload)
    if asyncio.iscoroutine(result):
        await result
