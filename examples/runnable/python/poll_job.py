"""Safe polling-loop example with terminal states and max-poll budget."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


SUCCESS_STATES = {"completed"}
FAILURE_STATES = {"failed", "cancelled"}


@dataclass(frozen=True)
class PollEvidence:
    polls: int
    statuses: tuple[str, ...]
    stop_reason: str


class PollTimeout(Exception):
    def __init__(self, evidence: PollEvidence):
        super().__init__(f"poll budget exhausted after {evidence.polls} polls")
        self.evidence = evidence


class JobFailed(Exception):
    def __init__(self, status: str, evidence: PollEvidence):
        super().__init__(f"job reached terminal failure state: {status}")
        self.status = status
        self.evidence = evidence


def poll_job(
    get_status: Callable[[str], str],
    job_id: str,
    *,
    max_polls: int,
    poll_interval_seconds: float = 0.0,
    sleep: Callable[[float], None] = lambda _seconds: None,
) -> PollEvidence:
    """Poll a job until success, terminal failure, or budget exhaustion."""

    if max_polls < 1:
        raise ValueError("max_polls must be at least 1")
    if poll_interval_seconds < 0:
        raise ValueError("poll_interval_seconds must be non-negative")

    statuses: list[str] = []
    for poll_number in range(1, max_polls + 1):
        status = get_status(job_id)
        statuses.append(status)
        evidence = PollEvidence(
            polls=poll_number,
            statuses=tuple(statuses),
            stop_reason=f"terminal-{status}",
        )
        if status in SUCCESS_STATES:
            return evidence
        if status in FAILURE_STATES:
            raise JobFailed(status, evidence)
        if poll_number < max_polls:
            sleep(poll_interval_seconds)

    raise PollTimeout(
        PollEvidence(
            polls=max_polls,
            statuses=tuple(statuses),
            stop_reason="poll-budget-exhausted",
        )
    )
