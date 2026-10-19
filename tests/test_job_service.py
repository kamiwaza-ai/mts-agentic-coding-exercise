from __future__ import annotations

from pathlib import Path

import pytest

from jobqueue.models import JobStatus
from jobqueue.repository import SQLiteJobRepository
from jobqueue.service import JobNotFoundError, JobOwnershipError, JobService


@pytest.fixture
def service(tmp_path: Path) -> JobService:
    return JobService(SQLiteJobRepository(tmp_path / "jobs.db"))


def test_enqueue_persists_and_gets_job(service: JobService) -> None:
    created = service.enqueue("resize image")

    loaded = service.get(created.id)

    assert loaded.id == created.id
    assert loaded.payload == "resize image"
    assert loaded.status is JobStatus.QUEUED
    assert loaded.worker_id is None
    assert loaded.result is None


def test_claim_next_uses_fifo_order(service: JobService) -> None:
    first = service.enqueue("first")
    second = service.enqueue("second")

    claimed = service.claim_next("worker-a")

    assert claimed is not None
    assert claimed.id == first.id
    assert claimed.status is JobStatus.RUNNING
    assert claimed.worker_id == "worker-a"
    assert service.get(second.id).status is JobStatus.QUEUED


def test_running_job_is_not_claimed_again(service: JobService) -> None:
    service.enqueue("only job")
    service.claim_next("worker-a")

    assert service.claim_next("worker-b") is None


def test_only_claiming_worker_can_complete_job(service: JobService) -> None:
    queued = service.enqueue("protected")
    service.claim_next("worker-a")

    with pytest.raises(JobOwnershipError):
        service.complete(queued.id, "worker-b", "not allowed")

    assert service.get(queued.id).status is JobStatus.RUNNING


def test_complete_records_result(service: JobService) -> None:
    queued = service.enqueue("finish me")
    service.claim_next("worker-a")

    completed = service.complete(queued.id, "worker-a", "done")

    assert completed.status is JobStatus.SUCCEEDED
    assert completed.result == "done"
    assert completed.worker_id == "worker-a"
    assert service.claim_next("worker-b") is None


def test_get_unknown_job_raises(service: JobService) -> None:
    with pytest.raises(JobNotFoundError):
        service.get("missing")


def test_jobs_survive_repository_reopen(tmp_path: Path) -> None:
    database = tmp_path / "jobs.db"
    created = JobService(SQLiteJobRepository(database)).enqueue("durable")

    reopened = JobService(SQLiteJobRepository(database))

    assert reopened.get(created.id).payload == "durable"
