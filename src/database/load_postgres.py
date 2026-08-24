from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.database.connection import get_engine
from src.logging_config import get_logger


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_FILE = PROJECT_ROOT / "data" / "processed" / "weather_cleaned.csv"

TABLE_NAME = "weather_hourly"

logger = get_logger(__name__)


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
            raise ValueError("Processed weather dataset is empty.")

        logger.info(
            "Processed dataset loaded with %d rows",
            len(dataframe),
        )

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

        records = dataframe.to_dict(orient="records")

        with engine.begin() as connection:
            connection.execute(upsert_sql, records)

        logger.info(
            "Successfully upserted %d rows into %s",
            len(dataframe),
            TABLE_NAME,
        )

        print(
            f"SUCCESS: Upserted {len(dataframe)} rows into {TABLE_NAME}"
        )

    except FileNotFoundError:
        logger.exception("Processed weather file was not found")
        raise

    except (pd.errors.ParserError, ValueError):
        logger.exception("Processed weather data is invalid")
        raise

    except SQLAlchemyError:
        logger.exception("PostgreSQL upsert failed")
        raise

    except Exception:
        logger.exception("Unexpected PostgreSQL load failure")
        raise


if __name__ == "__main__":
    load_weather_data()