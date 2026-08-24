import subprocess
import sys

from src.logging_config import get_logger


logger = get_logger(__name__)


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

        sys.exit(result.returncode)

    logger.info("Pipeline step completed successfully: %s", name)

    print(f"SUCCESS: {name}")


def main() -> None:
    logger.info("Starting complete weather data pipeline")

    python = sys.executable

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

    logger.info("Complete weather data pipeline finished successfully")

    print("\nPIPELINE COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()