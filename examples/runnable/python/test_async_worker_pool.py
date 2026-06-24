import asyncio
import unittest

from async_worker_pool import process_events


class AsyncWorkerPoolTests(unittest.IsolatedAsyncioTestCase):
    async def test_processes_events_with_bounded_concurrency(self):
        active = 0
        observed_max = 0

        async def handler(event):
            nonlocal active, observed_max
            active += 1
            observed_max = max(observed_max, active)
            await asyncio.sleep(0)
            active -= 1

        evidence = await process_events(range(20), handler, concurrency=4)

        self.assertEqual(evidence.total, 20)
        self.assertEqual(evidence.succeeded, 20)
        self.assertLessEqual(evidence.max_active_workers, 4)
        self.assertLessEqual(observed_max, 4)

    async def test_records_partial_failures_as_dead_letters(self):
        async def handler(event):
            if event in {2, 4}:
                raise RuntimeError("downstream rejected event")

        evidence = await process_events(range(6), handler, concurrency=3)

        self.assertEqual(evidence.succeeded, 4)
        self.assertEqual(evidence.failed, 2)
        self.assertEqual(evidence.dead_letters, ((2, "RuntimeError"), (4, "RuntimeError")))

    async def test_zero_input_finishes_without_workers(self):
        async def handler(event):
            raise AssertionError("handler should not run")

        evidence = await process_events([], handler, concurrency=2)

        self.assertEqual(evidence.stop_reason, "input-exhausted")
        self.assertEqual(evidence.max_active_workers, 0)


if __name__ == "__main__":
    unittest.main()
