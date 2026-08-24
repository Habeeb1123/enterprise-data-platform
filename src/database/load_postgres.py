from pathlib import Path

import pandas as pd
from sqlalchemy import BigInteger, DateTime, Float
from sqlalchemy.exc import SQLAlchemyError

from src.database.connection import get_engine
from src.logging_config import get_logger


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_FILE = PROJECT_ROOT / "data" / "processed" / "weather_cleaned.csv"

TABLE_NAME = "weather_hourly"

logger = get_logger(__name__)


def load_weather_data() -> None:
    logger.info("Starting PostgreSQL load")

    try:
        if not PROCESSED_FILE.exists():
            raise FileNotFoundError(
                f"Processed weather file not found: {PROCESSED_FILE}"
            )

        logger.info("Reading processed data from %s", PROCESSED_FILE)

        dataframe = pd.read_csv(
            PROCESSED_FILE,
            parse_dates=["timestamp"],
        )

        if dataframe.empty:
            raise ValueError("Processed weather dataset is empty.")

        logger.info(
            "Processed dataset loaded successfully with %d rows",
            len(dataframe),
        )

        logger.info("Creating PostgreSQL database connection")

        engine = get_engine()

        logger.info(
            "Loading data into PostgreSQL table: %s",
            TABLE_NAME,
        )

        dataframe.to_sql(
            TABLE_NAME,
            con=engine,
            if_exists="replace",
            index=False,
            dtype={
                "timestamp": DateTime(),
                "temperature_2m": Float(),
                "relative_humidity_2m": BigInteger(),
                "precipitation": Float(),
            },
        )

        logger.info(
            "Successfully loaded %d rows into %s",
            len(dataframe),
            TABLE_NAME,
        )

        print(
            f"SUCCESS: Loaded {len(dataframe)} rows into {TABLE_NAME}"
        )

    except FileNotFoundError:
        logger.exception("Processed weather file was not found")
        raise

    except (pd.errors.ParserError, ValueError):
        logger.exception("Processed weather data is invalid")
        raise

    except SQLAlchemyError:
        logger.exception("PostgreSQL database operation failed")
        raise

    except Exception:
        logger.exception("Unexpected PostgreSQL load failure")
        raise


if __name__ == "__main__":
    load_weather_data()