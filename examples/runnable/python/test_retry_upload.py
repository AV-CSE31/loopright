import unittest

from retry_upload import (
    PermanentUploadError,
    RetryBudgetExceeded,
    TransientUploadError,
    upload_with_retry,
)


class FakeClient:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0

    def upload(self, payload):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class RetryUploadTests(unittest.TestCase):
    def test_retries_transient_failure_and_records_evidence(self):
        sleeps = []
        client = FakeClient([TransientUploadError(), TransientUploadError(), "receipt-123"])

        result = upload_with_retry(
            client,
            b"payload",
            max_attempts=4,
            base_delay_seconds=0.5,
            sleep=sleeps.append,
        )

        self.assertEqual(result.receipt_id, "receipt-123")
        self.assertEqual(result.evidence.attempts, 3)
        self.assertEqual(result.evidence.stop_reason, "uploaded")
        self.assertEqual(sleeps, [0.5, 1.0])

    def test_stops_after_retry_budget_is_exhausted(self):
        client = FakeClient([TransientUploadError(), TransientUploadError(), TransientUploadError()])

        with self.assertRaises(RetryBudgetExceeded) as raised:
            upload_with_retry(client, b"payload", max_attempts=3)

        self.assertEqual(client.calls, 3)
        self.assertEqual(raised.exception.evidence.stop_reason, "retry-budget-exhausted")
        self.assertFalse(raised.exception.evidence.success)

    def test_does_not_retry_permanent_failure(self):
        client = FakeClient([PermanentUploadError()])

        with self.assertRaises(PermanentUploadError):
            upload_with_retry(client, b"payload", max_attempts=3)

        self.assertEqual(client.calls, 1)


if __name__ == "__main__":
    unittest.main()
