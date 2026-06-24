"""Safe async fan-out example with bounded workers and completion evidence."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Iterable


Handler = Callable[[Any], Awaitable[None]]


@dataclass(frozen=True)
class BatchEvidence:
    total: int
    succeeded: int
    failed: int
    max_active_workers: int
    stop_reason: str
    dead_letters: tuple[tuple[Any, str], ...]


async def process_events(
    events: Iterable[Any],
    handler: Handler,
    *,
    concurrency: int,
    timeout_seconds: float | None = None,
) -> BatchEvidence:
    """Process a finite event collection with bounded worker concurrency."""

    if concurrency < 1:
        raise ValueError("concurrency must be at least 1")

    event_list = list(events)
    if not event_list:
        return BatchEvidence(
            total=0,
            succeeded=0,
            failed=0,
            max_active_workers=0,
            stop_reason="input-exhausted",
            dead_letters=(),
        )

    queue: asyncio.Queue[Any] = asyncio.Queue()
    for event in event_list:
        queue.put_nowait(event)

    active_workers = 0
    max_active_workers = 0
    succeeded = 0
    dead_letters: list[tuple[Any, str]] = []
    lock = asyncio.Lock()

    async def worker() -> None:
        nonlocal active_workers, max_active_workers, succeeded
        for _ in range(len(event_list)):
            try:
                event = queue.get_nowait()
            except asyncio.QueueEmpty:
                return

            async with lock:
                active_workers += 1
                max_active_workers = max(max_active_workers, active_workers)
            try:
                await handler(event)
                async with lock:
                    succeeded += 1
            except Exception as error:
                dead_letters.append((event, type(error).__name__))
            finally:
                async with lock:
                    active_workers -= 1
                queue.task_done()

    worker_count = min(concurrency, len(event_list))
    tasks = [asyncio.create_task(worker()) for _ in range(worker_count)]
    try:
        if timeout_seconds is None:
            await asyncio.gather(*tasks)
        else:
            await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout_seconds)
    except TimeoutError:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        return BatchEvidence(
            total=len(event_list),
            succeeded=succeeded,
            failed=len(dead_letters),
            max_active_workers=max_active_workers,
            stop_reason="timeout",
            dead_letters=tuple(dead_letters),
        )

    return BatchEvidence(
        total=len(event_list),
        succeeded=succeeded,
        failed=len(dead_letters),
        max_active_workers=max_active_workers,
        stop_reason="input-exhausted",
        dead_letters=tuple(dead_letters),
    )
