from datetime import datetime, timedelta
import subprocess

from airflow import DAG
from airflow.operators.python import PythonOperator


PROJECT_DIR = "/opt/airflow/project"


def run_command(command: list[str]) -> None:
    subprocess.run(
        command,
        cwd=PROJECT_DIR,
        check=True,
    )


def ingest_weather() -> None:
    run_command(
        [
            "python",
            "-m",
            "src.ingestion.api_ingestion",
        ]
    )


def transform_weather() -> None:
    run_command(
        [
            "python",
            "-m",
            "src.transformation.clean_data",
        ]
    )


def load_postgres() -> None:
    run_command(
        [
            "python",
            "-m",
            "src.database.load_postgres",
        ]
    )


def run_tests() -> None:
    run_command(
        [
            "python",
            "-m",
            "pytest",
            "-v",
        ]
    )


default_args = {
    "owner": "data-engineering",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="weather_data_pipeline",
    description="Orchestrates the enterprise weather data pipeline",
    default_args=default_args,
    start_date=datetime(2026, 8, 24),
    schedule="0 6 * * *",
    catchup=False,
    tags=["data-engineering", "weather", "etl"],
) as dag:

    ingestion = PythonOperator(
        task_id="api_ingestion",
        python_callable=ingest_weather,
    )

    transformation = PythonOperator(
        task_id="data_transformation",
        python_callable=transform_weather,
    )

    postgres_load = PythonOperator(
        task_id="postgresql_load",
        python_callable=load_postgres,
    )

    automated_tests = PythonOperator(
        task_id="automated_tests",
        python_callable=run_tests,
    )

    ingestion >> transformation >> postgres_load >> automated_tests