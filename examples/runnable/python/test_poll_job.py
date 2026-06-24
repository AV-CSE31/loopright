import unittest

from poll_job import JobFailed, PollTimeout, poll_job


class StatusFeed:
    def __init__(self, statuses):
        self.statuses = list(statuses)
        self.calls = 0

    def __call__(self, job_id):
        self.calls += 1
        return self.statuses.pop(0)


class PollJobTests(unittest.TestCase):
    def test_stops_on_success_terminal_state(self):
        sleeps = []
        feed = StatusFeed(["queued", "running", "completed"])

        evidence = poll_job(feed, "job-1", max_polls=5, poll_interval_seconds=2.0, sleep=sleeps.append)

        self.assertEqual(evidence.stop_reason, "terminal-completed")
        self.assertEqual(evidence.statuses, ("queued", "running", "completed"))
        self.assertEqual(sleeps, [2.0, 2.0])

    def test_stops_on_failure_terminal_state(self):
        feed = StatusFeed(["queued", "failed"])

        with self.assertRaises(JobFailed) as raised:
            poll_job(feed, "job-2", max_polls=5)

        self.assertEqual(raised.exception.status, "failed")
        self.assertEqual(raised.exception.evidence.stop_reason, "terminal-failed")

    def test_stops_on_poll_budget_exhaustion(self):
        feed = StatusFeed(["queued", "running", "running"])

        with self.assertRaises(PollTimeout) as raised:
            poll_job(feed, "job-3", max_polls=3)

        self.assertEqual(raised.exception.evidence.polls, 3)
        self.assertEqual(raised.exception.evidence.stop_reason, "poll-budget-exhausted")


if __name__ == "__main__":
    unittest.main()
