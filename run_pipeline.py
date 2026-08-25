from datetime import datetime, timezone
import subprocess
import sys

from src.logging_config import get_logger
from src.monitoring.pipeline_monitor import record_pipeline_run


logger = get_logger(__name__)


class PipelineStepError(Exception):
    def __init__(self, step_name: str, exit_code: int):
        self.step_name = step_name
        self.exit_code = exit_code

        super().__init__(
            f"Pipeline step '{step_name}' failed with exit code {exit_code}"
        )


def run_step(name: str, command: list[str]) -> None:
    logger.info("Starting pipeline step: %s", name)

    print(f"\n=== {name} ===")

    try:
        result = subprocess.run(
            command,
            check=False,
        )

    except OSError:
        logger.exception("Failed to start pipeline step: %s", name)
        raise

    if result.returncode != 0:
        logger.error(
            "Pipeline step failed: %s with exit code %s",
            name,
            result.returncode,
        )

        print(f"\nFAILED: {name}")

        raise PipelineStepError(
            step_name=name,
            exit_code=result.returncode,
        )

    logger.info(
        "Pipeline step completed successfully: %s",
        name,
    )

    print(f"SUCCESS: {name}")


def main() -> None:
    started_at = datetime.now(timezone.utc)

    logger.info("Starting complete weather data pipeline")

    python = sys.executable

    try:
        run_step(
            "API ingestion",
            [
                python,
                "-m",
                "src.ingestion.api_ingestion",
            ],
        )

        run_step(
            "Data transformation",
            [
                python,
                "-m",
                "src.transformation.clean_data",
            ],
        )

        run_step(
            "PostgreSQL load",
            [
                python,
                "-m",
                "src.database.load_postgres",
            ],
        )

        run_step(
            "Automated tests",
            [
                python,
                "-m",
                "pytest",
                "-v",
            ],
        )

    except PipelineStepError as error:
        finished_at = datetime.now(timezone.utc)

        record_pipeline_run(
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            failed_step=error.step_name,
            exit_code=error.exit_code,
        )

        logger.error(
            "Complete weather data pipeline failed at step: %s",
            error.step_name,
        )

        sys.exit(error.exit_code)

    except Exception:
        finished_at = datetime.now(timezone.utc)

        record_pipeline_run(
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            failed_step="unexpected_error",
            exit_code=1,
        )

        logger.exception(
            "Complete weather data pipeline failed unexpectedly"
        )

        sys.exit(1)

    finished_at = datetime.now(timezone.utc)

    record_pipeline_run(
        status="success",
        started_at=started_at,
        finished_at=finished_at,
        failed_step=None,
        exit_code=0,
    )

    logger.info(
        "Complete weather data pipeline finished successfully"
    )

    print("\nPIPELINE COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()