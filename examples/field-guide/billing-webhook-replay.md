# Billing Webhook Replay

## User Prompt

```text
$loopright Review our Stripe webhook replay script. We need to replay three days of missed
invoice.paid and payment_failed events after an outage. The script must not double-credit
accounts or keep retrying invalid customer records.
```

## Risky Starting Point

```python
def replay(events):
    for event in events:
        while True:
            try:
                apply_billing_event(event)
                break
            except Exception:
                time.sleep(5)
```

## LoopRight Diagnosis

Verdict: Unsafe to run

Findings:

- P1: `while True` has no attempt budget, deadline, or no-progress stop.
- P1: `except Exception` retries permanent failures such as missing customers and invalid invoice state.
- P1: No idempotency key is named, so replay can double-credit or double-mark invoices after a process crash.
- P2: No reconciliation artifact proves every input event reached a terminal state.

## Loop Contract

| Element | Answer |
|---|---|
| Objective | Replay all eligible billing events from `2026-06-17T00:00Z` to `2026-06-20T00:00Z` exactly once per event id and produce a reconciliation report. |
| State | Event cursor, processed event ids, invoice idempotency records, retry count per event, terminal result per event. |
| Action | Load one bounded page of events, classify each event, apply idempotent billing update, record terminal status, checkpoint cursor. |
| Progress | Checkpoint advances monotonically and terminal event count increases after each page. |
| Invariant | A billing event id can create at most one ledger mutation for the same replay id. |
| Budget | Page size 500, max 4 attempts per transient event, max 45 minutes wall time, max provider retry delay 60 seconds. |
| Stop condition | Every event in the replay window is terminal: applied, skipped, permanent-failed, or dead-lettered. |
| Failure condition | Idempotency table unavailable, ledger mutation mismatch, permanent failure rate above 2%, or retry budget exhausted for more than 100 events. |
| Recovery | Resume from checkpoint, skip event ids already terminal for the replay id, dead-letter permanent failures with reason. |
| Evidence | `billing-replay-2026-06-20.json` with input count, applied count, skipped count, dead-letter count, ledger checksum, and sampled invoice ids. |

## Minimal Repair

```python
def replay(events, replay_id, checkpoint_store, ledger, report):
    for page in pages(events, size=500, after=checkpoint_store.cursor(replay_id)):
        for event in page:
            if ledger.already_applied(replay_id, event.id):
                report.skipped(event.id, "already-applied")
                continue
            try:
                apply_with_retry(event, replay_id=replay_id, max_attempts=4)
                report.applied(event.id)
            except PermanentBillingError as error:
                report.dead_letter(event.id, type(error).__name__)
            checkpoint_store.save(replay_id, page.last_cursor)
```

The exact implementation should use the project's existing retry/idempotency helpers when available.

## Required Evidence

- Unit test: permanent customer-not-found event is not retried.
- Unit test: transient provider timeout retries no more than 4 times.
- Integration test: replaying the same event twice produces one ledger mutation.
- Dry-run report: input count equals applied plus skipped plus dead-lettered.
- Operator artifact: reconciliation JSON attached to the incident ticket.
