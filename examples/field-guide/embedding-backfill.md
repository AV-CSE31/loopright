# Embedding Backfill

## User Prompt

```text
$loopright Design a safe embedding backfill for 42M knowledge-base documents.
We changed embedding models and need to re-index without losing search coverage
or blowing through the vendor quota.
```

## Risky Starting Point

```python
for doc in all_documents():
    vector = embeddings.create(doc.text)
    vector_store.upsert(doc.id, vector)
```

This looks harmless in a notebook. In production it has no checkpoint, no versioned output, no quota budget, and no way to prove search coverage after partial failure.

## LoopRight Diagnosis

Verdict: Repair needed

Findings:

- P1: The loop writes new vectors over old vectors without a model-version invariant.
- P1: No checkpoint or terminal status table means deploys and crashes can silently skip or duplicate work.
- P2: No rate-limit or daily spend budget is stated.
- P2: Completion evidence is only "script finished", which is not enough for search infrastructure.

## Loop Contract

| Element | Answer |
|---|---|
| Objective | Build embeddings for all active documents with model `text-embedding-3-large@2026-06` and make the new index queryable after coverage reaches 99.95%. |
| State | Document cursor, document version, embedding model version, attempt count, vector-write status, quota usage, coverage metrics. |
| Action | Read a bounded batch, skip unchanged documents already embedded for the target model version, create embeddings, write to a shadow index, record terminal status. |
| Progress | Terminal document count and shadow-index coverage increase after each batch. |
| Invariant | Existing production vectors are not overwritten until shadow index validation passes and cutover is approved. |
| Budget | Batch size 256, concurrency 16, max 3 transient attempts per document, daily vendor quota 3M docs, wall-clock deadline 36 hours. |
| Stop condition | All active documents are terminal and shadow-index coverage is at least 99.95%. |
| Failure condition | Vendor quota exhausted, permanent failure rate above 0.5%, checksum mismatch, or query smoke tests regress by more than 1%. |
| Recovery | Resume from cursor, skip target-version rows already written, retry transient failures next run, dead-letter permanent content errors. |
| Evidence | Backfill report with document counts, quota usage, dead-letter sample, index checksum, query smoke-test results, and cutover approval. |

## Minimal Repair

Use a versioned shadow index:

```text
source documents -> bounded batch -> embedding API -> shadow index kb_v2026_06
                 -> terminal status table -> coverage report -> read-only query smoke test
```

Do not switch production reads until the evidence artifact exists and the search owner approves cutover.

## Required Evidence

- Report includes `total_active`, `embedded_target_version`, `dead_lettered`, `skipped_unchanged`, and `coverage_percent`.
- Retry metrics separate transient provider errors from permanent content errors.
- Shadow index query smoke tests use a fixed query set and compare against baseline relevance.
- A rollback plan exists: keep old index alias until post-cutover health checks pass.
