from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_demo_runs_end_to_end(tmp_path: Path) -> None:
    environment = os.environ.copy()
    source = Path(__file__).parents[1] / "src"
    environment["PYTHONPATH"] = str(source)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "jobqueue.demo",
            "--database",
            str(tmp_path / "demo.db"),
        ],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert completed.returncode == 0, completed.stderr
    assert "claimed" in completed.stdout
    assert "succeeded" in completed.stdout
