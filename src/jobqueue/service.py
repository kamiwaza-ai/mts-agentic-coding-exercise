from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from .models import Job, JobStatus
from .repository import SQLiteJobRepository


class JobNotFoundError(LookupError):
    pass


class JobOwnershipError(RuntimeError):
    pass


class JobService:
    def __init__(self, repository: SQLiteJobRepository) -> None:
        self.repository = repository

    def enqueue(self, payload: str) -> Job:
        now = datetime.now(UTC)
        job = Job(
            id=str(uuid4()),
            payload=payload,
            status=JobStatus.QUEUED,
            worker_id=None,
            result=None,
            created_at=now,
            updated_at=now,
        )
        return self.repository.add(job)

    def claim_next(self, worker_id: str) -> Job | None:
        return self.repository.claim_next(worker_id, datetime.now(UTC))

    def complete(self, job_id: str, worker_id: str, result: str) -> Job:
        existing = self.get(job_id)
        if existing.status is not JobStatus.RUNNING or existing.worker_id != worker_id:
            raise JobOwnershipError(f"worker {worker_id!r} does not own running job {job_id!r}")

        completed = self.repository.complete(
            job_id,
            worker_id,
            result,
            datetime.now(UTC),
        )
        if completed is None:
            raise JobOwnershipError(f"worker {worker_id!r} no longer owns job {job_id!r}")
        return completed

    def get(self, job_id: str) -> Job:
        job = self.repository.get(job_id)
        if job is None:
            raise JobNotFoundError(job_id)
        return job
