# Example Task: Async Batch Processor

## User Prompt

Use `$loopright` to improve an async loop that processes 50,000 URLs.

## Risky Starting Point

```python
async def fetch_all(urls):
    return await asyncio.gather(*(fetch(url) for url in urls))
```

## LoopRight Classification

Async concurrent loop.

## Findings

- **P1:** The code creates one task per URL, so large input can exhaust memory, sockets, or rate limits.
- **P1:** Partial failure behavior is implicit because default `gather` cancels or raises without a result policy.
- **P2:** No progress evidence is returned beyond the final list.

## Loop Contract

| Element | Answer |
|---|---|
| Objective | Fetch every URL with bounded concurrency and report per-item success or failure. |
| State | Pending URLs, active tasks, completed results, failed results. |
| Action | Fetch one URL and record its result. |
| Progress | Completed plus failed count increases until all inputs are terminal. |
| Invariant | Active fetches never exceed the configured concurrency limit. |
| Budget | Concurrency limit of 20 and caller cancellation. |
| Stop condition | Every input URL has success or failure result. |
| Failure condition | Caller cancellation or fatal configuration error. |
| Recovery | Record per-URL failures; only cancel siblings for fatal errors. |
| Evidence | Return counts, result records, failure records, and max observed concurrency in tests. |

## Recommended Shape

Use a queue or semaphore and define whether individual failures are collected or fatal.

```python
async def fetch_all_bounded(urls, *, limit=20):
    semaphore = asyncio.Semaphore(limit)
    results = []

    async def run_one(url):
        async with semaphore:
            try:
                return {"url": url, "ok": True, "value": await fetch(url)}
            except FetchError as exc:
                return {"url": url, "ok": False, "error": str(exc)}

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(run_one(url)) for url in urls]

    return [task.result() for task in tasks]
```

## Evidence

- Test zero URLs returns an empty list.
- Test max active fetches never exceeds `limit`.
- Test individual fetch failure is represented in output.
- Test cancellation propagates.

