# Autonomous Quant Research Loop

## User Prompt

```text
$loopright Design a self-improving quant trading loop that ingests market data,
generates candidate signals, verifies them independently, paper-trades only
verified signals, monitors risk, and writes lessons back to memory.
```

This example is intentionally framed as a research and paper-trading loop. Do not use it as a real-money trading bot design without institutional risk controls, approvals, and regulatory review.

## Risky Starting Point

```python
while True:
    data = fetch_market_data()
    signal = agent.generate_signal(data)
    if agent.says_signal_is_good(signal):
        broker.send_order(signal)
    agent.write_lesson_from_last_trade()
```

## LoopRight Diagnosis

Verdict: Unsafe to run

Findings:

- P1: The same agent generates and approves the signal, so verification is not independent.
- P1: Real broker side effects happen before paper-trading evidence, idempotency, approval, or kill-switch checks.
- P1: State and lessons are implicit, so stale data, corrupt memory, and overfit rules can silently compound.
- P2: There is no trigger, cadence, runtime budget, capital/risk boundary, or no-action terminal state.
- P2: Completion evidence is missing: no backtest artifact, verifier verdict, paper order id, audit log, or risk-monitor record.

## Loop Contract

| Element | Answer |
|---|---|
| Objective | Generate candidate trading signals from approved data, accept only independently verified signals, paper-trade accepted signals, and record auditable outcomes without placing real-money orders. |
| State | Trigger id, market data snapshot hash, research state, candidate signal, verifier verdict, paper order ids, open paper positions, risk metrics, lesson queue, and audit log. |
| Action | Wake on data update, ingest data, generate one candidate signal, run independent verification, paper-trade only accepted signals, update risk state, and queue lessons for review. |
| Progress | Verified signal decisions and paper-trade outcome records accumulate while unresolved candidates and unreviewed lessons decrease. |
| Invariant | Real broker connectors remain disabled, maker and checker are separate, paper orders use idempotency keys, data versions are recorded, and lessons do not become rules until reviewed. |
| Budget | Max one research pass per data trigger, max 20 candidates per day, max 30 minute run time, max paper exposure per signal 2%, max drawdown threshold 5%, and fixed connector rate limits. |
| Stop condition | No eligible data update exists, every candidate is accepted/rejected/dead-lettered, risk monitor trips, approval is required, or the daily candidate/runtime budget is exhausted. |
| Failure condition | Verifier rejects the signal, backtest fails acceptance constraints, data snapshot is stale, paper connector idempotency fails, risk threshold is breached, or audit log write fails. |
| Recovery | Abort side effects, mark candidate rejected or dead-lettered, close paper exposure when the risk monitor trips, quarantine lessons for review, and require human approval before enabling any live connector. |
| Evidence | Data snapshot hash, signal proposal, independent verifier verdict, backtest metrics, paper order ids, risk-monitor status, rejected/dead-lettered candidates, reviewed lessons, and audit log location. |

## Minimal Repair

Use five bounded subloops, each with its own state and evidence:

```text
data ingestion loop
  -> writes versioned market snapshot and completeness report

signal generation loop
  -> reads approved snapshot and proposes one candidate at a time

independent verifier loop
  -> checks backtest, leakage, costs, slippage, drawdown, and out-of-sample evidence

paper execution loop
  -> submits only verified signals through paper connector with idempotency key

risk monitor loop
  -> watches paper exposure, drawdown, stale data, and connector failures; can freeze the other loops
```

Example paper-trading decision flow:

```python
snapshot = ingest_market_data(trigger_id)
candidate = maker.propose_signal(snapshot, max_candidates=20)
verdict = checker.verify_signal(
    candidate,
    required_metrics={
        "out_of_sample_years": 2,
        "max_drawdown": 0.10,
        "transaction_costs_included": True,
        "no_data_leakage": True,
    },
)

if risk_monitor.tripped():
    audit.stop("risk-monitor-tripped")
elif verdict.accepted:
    paper_order = paper_broker.submit(candidate, idempotency_key=verdict.signal_id)
    audit.record(candidate, verdict, paper_order)
else:
    audit.reject(candidate, verdict.reason)

lesson_queue.add(candidate.outcome_summary(), requires_review=True)
```

## Required Evidence

- Data snapshot report: timestamp, source, completeness, symbol universe, and hash.
- Signal proposal: hypothesis, feature list, data version, expected holding period, and risk assumptions.
- Independent verifier verdict: backtest command, out-of-sample period, transaction cost model, slippage model, drawdown, and leakage checks.
- Paper execution record: paper order id, idempotency key, position size, and no live-broker connector used.
- Risk monitor record: exposure, drawdown, stale-data status, kill-switch status, and stop reason when triggered.
- Memory governance record: proposed lesson, evidence behind it, reviewer approval, and whether it became a future rule.
