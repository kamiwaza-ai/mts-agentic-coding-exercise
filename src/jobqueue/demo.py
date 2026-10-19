from __future__ import annotations

import argparse
from pathlib import Path

from .repository import SQLiteJobRepository
from .service import JobService


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local job queue demo")
    parser.add_argument("--database", type=Path, default=Path("jobs.db"))
    args = parser.parse_args()

    service = JobService(SQLiteJobRepository(args.database))
    service.enqueue("generate daily report")
    claimed = service.claim_next("demo-worker")
    if claimed is None:
        raise RuntimeError("expected a queued job")
    print(f"claimed {claimed.id} by {claimed.worker_id}")
    completed = service.complete(claimed.id, "demo-worker", "report ready")
    print(f"{completed.status.value}: {completed.result}")


if __name__ == "__main__":
    main()
