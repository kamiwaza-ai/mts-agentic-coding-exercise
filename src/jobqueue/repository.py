from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from .models import Job, JobStatus


class SQLiteJobRepository:
    def __init__(self, database: str | Path) -> None:
        self.database = str(database)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL,
                    worker_id TEXT,
                    result TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def add(self, job: Job) -> Job:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO jobs (
                    id, payload, status, worker_id, result, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job.id,
                    job.payload,
                    job.status.value,
                    job.worker_id,
                    job.result,
                    job.created_at.isoformat(),
                    job.updated_at.isoformat(),
                ),
            )
        return job

    def get(self, job_id: str) -> Job | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return self._to_job(row) if row is not None else None

    def claim_next(self, worker_id: str, now: datetime) -> Job | None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                """
                SELECT * FROM jobs
                WHERE status = ?
                ORDER BY created_at, rowid
                LIMIT 1
                """,
                (JobStatus.QUEUED.value,),
            ).fetchone()
            if row is None:
                return None
            connection.execute(
                """
                UPDATE jobs
                SET status = ?, worker_id = ?, updated_at = ?
                WHERE id = ?
                """,
                (JobStatus.RUNNING.value, worker_id, now.isoformat(), row["id"]),
            )
            claimed = connection.execute("SELECT * FROM jobs WHERE id = ?", (row["id"],)).fetchone()
        return self._to_job(claimed)

    def complete(self, job_id: str, worker_id: str, result: str, now: datetime) -> Job | None:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE jobs
                SET status = ?, result = ?, updated_at = ?
                WHERE id = ? AND status = ? AND worker_id = ?
                """,
                (
                    JobStatus.SUCCEEDED.value,
                    result,
                    now.isoformat(),
                    job_id,
                    JobStatus.RUNNING.value,
                    worker_id,
                ),
            )
            if cursor.rowcount == 0:
                return None
            row = connection.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return self._to_job(row)

    @staticmethod
    def _to_job(row: sqlite3.Row) -> Job:
        return Job(
            id=row["id"],
            payload=row["payload"],
            status=JobStatus(row["status"]),
            worker_id=row["worker_id"],
            result=row["result"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
