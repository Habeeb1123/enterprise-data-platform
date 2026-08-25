from pathlib import Path
import json
from statistics import mean


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MONITORING_FILE = PROJECT_ROOT / "logs" / "pipeline_runs.jsonl"


def load_pipeline_runs() -> list[dict]:
    """Load pipeline monitoring records from the JSONL file."""

    if not MONITORING_FILE.exists():
        return []

    records = []

    with MONITORING_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                records.append(json.loads(line))

    return records


def generate_health_report(records: list[dict]) -> dict:
    """Calculate pipeline health metrics."""

    if not records:
        return {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "success_rate": 0.0,
            "average_duration_seconds": 0.0,
            "latest_status": None,
            "latest_run": None,
            "last_successful_run": None,
            "last_failed_run": None,
        }

    successful_runs = [
        record for record in records
        if record["status"] == "success"
    ]

    failed_runs = [
        record for record in records
        if record["status"] == "failed"
    ]

    durations = [
        record["duration_seconds"]
        for record in records
        if record.get("duration_seconds") is not None
    ]

    total_runs = len(records)

    success_rate = (
        len(successful_runs) / total_runs
    ) * 100

    average_duration = (
        mean(durations)
        if durations
        else 0.0
    )

    return {
        "total_runs": total_runs,
        "successful_runs": len(successful_runs),
        "failed_runs": len(failed_runs),
        "success_rate": round(success_rate, 2),
        "average_duration_seconds": round(
            average_duration,
            3,
        ),
        "latest_status": records[-1]["status"],
        "latest_run": records[-1],
        "last_successful_run": (
            successful_runs[-1]
            if successful_runs
            else None
        ),
        "last_failed_run": (
            failed_runs[-1]
            if failed_runs
            else None
        ),
    }


def print_health_report(report: dict) -> None:
    """Print a human-readable pipeline health report."""

    print("\n=== PIPELINE HEALTH REPORT ===")
    print(f"Total runs: {report['total_runs']}")
    print(f"Successful runs: {report['successful_runs']}")
    print(f"Failed runs: {report['failed_runs']}")
    print(f"Success rate: {report['success_rate']:.2f}%")
    print(
        "Average duration: "
        f"{report['average_duration_seconds']:.3f} seconds"
    )
    print(f"Latest status: {report['latest_status']}")

    last_successful_run = report["last_successful_run"]

    if last_successful_run:
        print(
            "Last successful run: "
            f"{last_successful_run['finished_at']}"
        )

    last_failed_run = report["last_failed_run"]

    if last_failed_run:
        print(
            "Last failed run: "
            f"{last_failed_run['finished_at']}"
        )
        print(
            "Last failed step: "
            f"{last_failed_run['failed_step']}"
        )


def main() -> None:
    records = load_pipeline_runs()
    report = generate_health_report(records)
    print_health_report(report)


if __name__ == "__main__":
    main()