# Current design

The starter is a deliberately small local service. `JobService` owns the application behavior,
and `SQLiteJobRepository` owns storage. Each repository operation opens its own SQLite connection.

The current lifecycle is deliberately incomplete:

```text
queued -> running -> succeeded
```

`claim_next` uses a SQLite write transaction to select the oldest queued job and mark it running.
`complete` requires the worker identifier stored on that job. The schema records timestamps for
diagnostics, but the service reads the wall clock directly and does not attach an expiration to a
claim.

The service may be constructed in multiple local processes against the same SQLite file. Worker
identifiers are operational labels, not unique sessions, and may be reused after a worker restarts.

## Operational problem

A worker can stop after claiming a job. Because `running` has no recovery path, the job remains
stuck. Two approaches have been discussed:

- reclaim expired work when a worker asks for the next job; or
- run a periodic process that moves abandoned jobs back to the queue.

Neither approach has been selected. The exercise does not require a background process. Consider
atomicity, ownership, and stale writes when choosing a design.

Operators have also observed that repeatedly abandoned work can keep returning ahead of newer jobs.
The requested retry budget is intended to preserve queue progress without introducing a separate
dead-letter service.

Workers sometimes need to extend a legitimate claim while processing takes longer than expected.
Operators also need to cancel queued or running work. Those actions can arrive at the same time as
recovery or completion from another process, so reading a job and then updating it unconditionally
is not sufficient. The requested behavior deliberately leaves the public API and transaction
boundaries for the candidate to design.

[`TASK.md`](../TASK.md) is the source of truth when a possible future design goes beyond the
required behavior.
