# Make the job lifecycle safe under retries and concurrency

## Background

The service currently allows a worker to claim a queued job and later mark it complete. If the
worker crashes after claiming the job, that job remains in `running` forever. Operators must edit
the database manually before another worker can make progress.

Implement lease-based recovery with renewal, cancellation, and a bounded retry policy. The service
runs in more than one local process against the same SQLite database, and worker identifiers may be
reused after a restart. Your solution must protect the job from stale workers, make terminal-state
races safe, and prevent repeatedly abandoned work from blocking the rest of the queue.

## Required behavior

Your implementation must make these behaviors observable and testable.

### Lease ownership and recovery

1. Claiming a queued job gives that specific claim a time-limited lease.
2. Another worker cannot claim the job while the lease is valid.
3. At the lease-expiration boundary, the claim is expired and the job may be reclaimed.
4. Worker identity alone is not proof of ownership. A worker holding an earlier claim cannot
   complete the job after a reclaim, including when the same worker identifier is reused.
5. An expired claim cannot complete, even if no other worker has reclaimed the job yet.

### Renewal and cancellation

6. A worker may renew its current, unexpired claim. Renewal extends the lease and preserves that
   claim's authority to complete the job.
7. An expired or superseded claim cannot be renewed. Renewal must not resurrect a claim that loses
   a race with recovery.
8. A queued or running job may be cancelled. Cancellation is idempotent and terminal: a cancelled
   job can never be claimed, renewed, completed, or failed by retry exhaustion.
9. Cancellation cannot overwrite a job that has already succeeded or failed.
10. If cancellation and completion race, exactly one terminal transition wins. The losing caller
    must receive a clear conflict rather than an apparently successful stale result.

### Retry budget and queue progress

11. A job may be claimed at most three times. The initial claim and every reclaim each consume one
   attempt.
12. If the third lease expires, the job becomes terminally `failed`, records a useful failure reason,
   and can never be claimed or completed again.
13. Encountering an expired job that has exhausted its attempts must not prevent the same
   `claim_next` call from claiming the next eligible job. An abandoned old job must not starve newer
   work.
14. Jobs remain ordered by their original enqueue order when choosing among eligible queued or
   reclaimable jobs.

### Atomicity and compatibility

15. Two independently constructed service instances using the same SQLite file may try to claim,
    reclaim, renew, cancel, or complete work concurrently. Conflicting state transitions must be
    serialized and preserve the invariants above.
16. Expiration cleanup, retry exhaustion, and selection of the next job must appear atomic to callers.
17. Time-dependent tests do not sleep or wait for wall-clock time. Concurrency tests should use
    deterministic coordination rather than timing assumptions.
18. Existing enqueue, retrieval, completion, FIFO, and persistence behavior remains sound.

Demonstrate the completed behavior at the end of the recording. Add tests that establish the
invariants you consider material.

## Design freedom

You may change the schema, models, repository, service interface, demo, and tests. Choose how to:

- represent lease duration, expiration, attempt count, and terminal failure;
- identify the currently valid claim;
- inject or control time in tests;
- perform lazy recovery and retry exhaustion;
- expose renewal and cancellation through a coherent public interface;
- preserve queue progress when older work is exhausted;
- coordinate competing transitions through SQLite; and
- communicate expired, stale, cancelled, and terminal operations.

Document interface changes and assumptions in [`NOTES.md`](NOTES.md). Prefer a small coherent
solution to broad unfinished infrastructure. If you do not finish everything, leave the repository
in a runnable state and explain the next safe increment.

## Constraints

- Keep the solution local and runnable with Python and SQLite.
- Do not call an LLM, paid API, or external service from the implemented application.
- Do not require Docker or a server to run the tests.
- Do not add a background service merely to satisfy the exercise.
- Do not add production migrations for databases created by this starter repository.

Automatic worker heartbeats, distributed coordination outside SQLite, configurable retry policies,
and a production deployment are out of scope. You may discuss them as follow-up work.
