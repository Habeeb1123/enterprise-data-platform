from pathlib import Path
import json

import pandas as pd

from src.logging_config import get_logger


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

logger = get_logger(__name__)


def get_latest_raw_file() -> Path:
    files = list(RAW_DATA_DIR.glob("weather_*.json"))

    if not files:
        logger.error("No raw weather files found in %s", RAW_DATA_DIR)
        raise FileNotFoundError("No raw weather files found.")

    latest_file = max(files, key=lambda file: file.stat().st_mtime)

    logger.info("Latest raw weather file selected: %s", latest_file)

    return latest_file


def load_raw_data(file_path: Path) -> dict:
    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

    except FileNotFoundError:
        logger.exception("Raw weather file does not exist: %s", file_path)
        raise

    except json.JSONDecodeError:
        logger.exception("Raw weather file contains invalid JSON: %s", file_path)
        raise

    except OSError:
        logger.exception("Failed to read raw weather file: %s", file_path)
        raise

    logger.info("Raw weather data loaded successfully")

    return data


def transform_weather_data(data: dict) -> pd.DataFrame:
    try:
        hourly = data["hourly"]

        required_fields = [
            "time",
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
        ]

        missing_fields = [
            field for field in required_fields if field not in hourly
        ]

        if missing_fields:
            raise KeyError(
                f"Missing required hourly fields: {missing_fields}"
            )

        dataframe = pd.DataFrame(
            {
                "timestamp": hourly["time"],
                "temperature_2m": hourly["temperature_2m"],
                "relative_humidity_2m": hourly["relative_humidity_2m"],
                "precipitation": hourly["precipitation"],
            }
        )

        original_rows = len(dataframe)

        dataframe["timestamp"] = pd.to_datetime(
            dataframe["timestamp"],
            errors="coerce",
        )

        dataframe = dataframe.drop_duplicates()

        dataframe = dataframe.dropna(
            subset=[
                "timestamp",
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
            ]
        )

        dataframe = dataframe.sort_values("timestamp").reset_index(drop=True)

        cleaned_rows = len(dataframe)

        logger.info(
            "Transformation completed: %s raw rows -> %s cleaned rows",
            original_rows,
            cleaned_rows,
        )

        return dataframe

    except KeyError:
        logger.exception("Required weather field missing")
        raise

    except (TypeError, ValueError):
        logger.exception("Weather data transformation failed")
        raise


def save_processed_data(dataframe: pd.DataFrame) -> Path:
    output_file = PROCESSED_DATA_DIR / "weather_cleaned.csv"

    try:
        dataframe.to_csv(output_file, index=False)

    except OSError:
        logger.exception("Failed to save processed weather data")
        raise

    logger.info("Processed weather data saved to %s", output_file)

    return output_file


def main() -> None:
    try:
        logger.info("Starting weather transformation")

        raw_file = get_latest_raw_file()
        data = load_raw_data(raw_file)
        dataframe = transform_weather_data(data)
        output_file = save_processed_data(dataframe)

        logger.info("Weather transformation completed successfully")

        print(f"Loading: {raw_file}")
        print(f"Rows processed: {len(dataframe)}")
        print(f"SUCCESS: Cleaned data saved to {output_file}")

    except Exception as exc:
        logger.exception("Weather transformation pipeline failed")
        print(f"ERROR: Weather transformation failed: {exc}")
        raise


if __name__ == "__main__":
    main()