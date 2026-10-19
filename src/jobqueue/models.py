from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"


@dataclass(frozen=True, slots=True)
class Job:
    id: str
    payload: str
    status: JobStatus
    worker_id: str | None
    result: str | None
    created_at: datetime
    updated_at: datetime
