from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.database.connection import get_engine
from src.logging_config import get_logger


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "weather_cleaned.csv"
)

ANALYTICS_SQL_FILE = (
    PROJECT_ROOT
    / "sql"
    / "create_weather_analytics_views.sql"
)

TABLE_NAME = "weather_hourly"

logger = get_logger(__name__)


def load_analytics_sql() -> list[str]:
    if not ANALYTICS_SQL_FILE.exists():
        raise FileNotFoundError(
            f"Analytics SQL file not found: {ANALYTICS_SQL_FILE}"
        )

    sql_script = ANALYTICS_SQL_FILE.read_text(
        encoding="utf-8"
    )

    statements = [
        statement.strip()
        for statement in sql_script.split(";")
        if statement.strip()
    ]

    if not statements:
        raise ValueError(
            "Analytics SQL file contains no executable statements."
        )

    return statements


def load_weather_data() -> None:
    logger.info("Starting PostgreSQL upsert")

    try:
        if not PROCESSED_FILE.exists():
            raise FileNotFoundError(
                f"Processed weather file not found: {PROCESSED_FILE}"
            )

        dataframe = pd.read_csv(
            PROCESSED_FILE,
            parse_dates=["timestamp"],
        )

        if dataframe.empty:
            raise ValueError(
                "Processed weather dataset is empty."
            )

        logger.info(
            "Processed dataset loaded with %d rows",
            len(dataframe),
        )

        analytics_statements = load_analytics_sql()

        engine = get_engine()

        upsert_sql = text(
            """
            INSERT INTO weather_hourly (
                timestamp,
                temperature_2m,
                relative_humidity_2m,
                precipitation
            )
            VALUES (
                :timestamp,
                :temperature_2m,
                :relative_humidity_2m,
                :precipitation
            )
            ON CONFLICT (timestamp)
            DO UPDATE SET
                temperature_2m = EXCLUDED.temperature_2m,
                relative_humidity_2m = EXCLUDED.relative_humidity_2m,
                precipitation = EXCLUDED.precipitation;
            """
        )

        records = dataframe.to_dict(
            orient="records"
        )

        with engine.begin() as connection:
            connection.execute(
                upsert_sql,
                records,
            )

            logger.info(
                "Successfully upserted %d rows into %s",
                len(dataframe),
                TABLE_NAME,
            )

            logger.info(
                "Creating or refreshing analytics views"
            )

            for statement in analytics_statements:
                connection.exec_driver_sql(
                    statement
                )

        logger.info(
            "Analytics views created successfully"
        )

        print(
            f"SUCCESS: Upserted {len(dataframe)} rows "
            f"into {TABLE_NAME}"
        )

        print(
            "SUCCESS: Analytics views created successfully"
        )

    except FileNotFoundError:
        logger.exception(
            "Required pipeline file was not found"
        )
        raise

    except (
        pd.errors.ParserError,
        ValueError,
    ):
        logger.exception(
            "Pipeline data or SQL configuration is invalid"
        )
        raise

    except SQLAlchemyError:
        logger.exception(
            "PostgreSQL load or analytics view creation failed"
        )
        raise

    except Exception:
        logger.exception(
            "Unexpected PostgreSQL load failure"
        )
        raise


if __name__ == "__main__":
    load_weather_data()