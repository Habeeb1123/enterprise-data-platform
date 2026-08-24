import subprocess
import sys


def run_step(name: str, command: list[str]) -> None:
    print(f"\n=== {name} ===")

    result = subprocess.run(command)

    if result.returncode != 0:
        print(f"\nFAILED: {name}")
        sys.exit(result.returncode)

    print(f"SUCCESS: {name}")


def main() -> None:
    python = sys.executable

    run_step(
        "API ingestion",
        [python, "src/ingestion/api_ingestion.py"],
    )

    run_step(
        "Data transformation",
        [python, "src/transformation/clean_data.py"],
    )

    run_step(
        "PostgreSQL load",
        [python, "src/database/load_postgres.py"],
    )

    run_step(
        "Automated tests",
        [python, "-m", "pytest", "-v"],
    )

    print("\nPIPELINE COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()