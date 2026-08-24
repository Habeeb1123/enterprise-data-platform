from pathlib import Path
from datetime import datetime
import json

import requests

from src.logging_config import get_logger


API_URL = "https://api.open-meteo.com/v1/forecast"

PARAMS = {
    "latitude": 54.9069,
    "longitude": -1.3838,
    "hourly": "temperature_2m,relative_humidity_2m,precipitation",
    "timezone": "Europe/London",
}


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

logger = get_logger(__name__)


def fetch_weather_data() -> dict:
    logger.info("Starting API request")

    try:
        response = requests.get(
            API_URL,
            params=PARAMS,
            timeout=30,
        )

        response.raise_for_status()

    except requests.Timeout:
        logger.exception("API request timed out")
        raise

    except requests.ConnectionError:
        logger.exception("Failed to connect to weather API")
        raise

    except requests.HTTPError:
        logger.exception("Weather API returned an HTTP error")
        raise

    except requests.RequestException:
        logger.exception("Unexpected API request error")
        raise

    logger.info(
        "API request successful with status code %s",
        response.status_code,
    )

    return response.json()


def save_raw_data(data: dict) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RAW_DATA_DIR / f"weather_{timestamp}.json"

    try:
        with output_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    except OSError:
        logger.exception("Failed to save raw weather data")
        raise

    logger.info("Raw weather data saved to %s", output_file)

    return output_file


def main() -> None:
    try:
        data = fetch_weather_data()
        output_file = save_raw_data(data)

        logger.info("API ingestion completed successfully")

        print(f"SUCCESS: Raw data saved to {output_file}")

    except Exception as exc:
        logger.exception("API ingestion failed")
        print(f"ERROR: API ingestion failed: {exc}")
        raise


if __name__ == "__main__":
    main()