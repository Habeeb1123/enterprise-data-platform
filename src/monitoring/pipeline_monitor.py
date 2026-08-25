from datetime import datetime, timezone
from pathlib import Path
import json


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MONITORING_DIR = PROJECT_ROOT / "logs"
MONITORING_FILE = MONITORING_DIR / "pipeline_runs.jsonl"

MONITORING_DIR.mkdir(parents=True, exist_ok=True)


def record_pipeline_run(
    status: str,
    started_at: datetime,
    finished_at: datetime,
    failed_step: str | None = None,
    exit_code: int | None = None,
) -> None:
    duration_seconds = (finished_at - started_at).total_seconds()

    record = {
        "status": status,
        "started_at": started_at.astimezone(timezone.utc).isoformat(),
        "finished_at": finished_at.astimezone(timezone.utc).isoformat(),
        "duration_seconds": round(duration_seconds, 3),
        "failed_step": failed_step,
        "exit_code": exit_code,
    }

    with MONITORING_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")