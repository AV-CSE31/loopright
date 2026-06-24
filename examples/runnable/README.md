# Runnable LoopRight Examples

These examples show unsafe loop ideas repaired into bounded, testable implementations with completion evidence. They use only the Python standard library.

Run all examples:

```bash
python -m unittest discover -s examples/runnable/python -p "test_*.py"
```

What the examples prove:

- `retry_upload.py`: retry only transient failures, stop at `max_attempts`, preserve evidence.
- `poll_job.py`: poll with terminal states and `max_polls`.
- `async_worker_pool.py`: process finite input with bounded workers, partial-failure evidence, and timeout behavior.
