"""Safe retry-loop example with explicit budget and evidence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol


class TransientUploadError(Exception):
    """Raised for retryable upload failures."""


class PermanentUploadError(Exception):
    """Raised for failures that must not be retried."""


@dataclass(frozen=True)
class RetryEvidence:
    attempts: int
    success: bool
    stop_reason: str
    errors: tuple[str, ...]


class RetryBudgetExceeded(Exception):
    def __init__(self, evidence: RetryEvidence):
        super().__init__(f"upload retry budget exhausted after {evidence.attempts} attempts")
        self.evidence = evidence


class UploadClient(Protocol):
    def upload(self, payload: bytes) -> str:
        """Upload a payload and return a receipt id."""


@dataclass(frozen=True)
class UploadResult:
    receipt_id: str
    evidence: RetryEvidence


def upload_with_retry(
    client: UploadClient,
    payload: bytes,
    *,
    max_attempts: int,
    base_delay_seconds: float = 0.0,
    sleep: Callable[[float], None] = lambda _seconds: None,
    jitter: Callable[[int], float] = lambda _attempt: 0.0,
) -> UploadResult:
    """Retry transient upload failures and stop with evidence."""

    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
    if base_delay_seconds < 0:
        raise ValueError("base_delay_seconds must be non-negative")

    errors: list[str] = []
    for attempt in range(1, max_attempts + 1):
        try:
            receipt_id = client.upload(payload)
            return UploadResult(
                receipt_id=receipt_id,
                evidence=RetryEvidence(
                    attempts=attempt,
                    success=True,
                    stop_reason="uploaded",
                    errors=tuple(errors),
                ),
            )
        except TransientUploadError as error:
            errors.append(type(error).__name__)
            if attempt == max_attempts:
                break
            delay = base_delay_seconds * (2 ** (attempt - 1)) + jitter(attempt)
            sleep(delay)

    raise RetryBudgetExceeded(
        RetryEvidence(
            attempts=max_attempts,
            success=False,
            stop_reason="retry-budget-exhausted",
            errors=tuple(errors),
        )
    )
