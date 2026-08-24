from pathlib import Path
from datetime import datetime
import json
import logging
import requests


API_URL = "https://api.open-meteo.com/v1/forecast"

PARAMS = {
    "latitude": 54.9069,
    "longitude": -1.3838,
    "hourly": "temperature_2m,relative_humidity_2m,precipitation",
    "timezone": "Europe/London",
}


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

LOG_DIR = PROJECT_ROOT / "logs"


RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

LOG_DIR.mkdir(parents=True, exist_ok=True)


logging.basicConfig(
    filename=LOG_DIR / "ingestion.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def fetch_weather_data() -> dict:
    logging.info("Starting API request")

    response = requests.get(
        API_URL,
        params=PARAMS,
        timeout=30,
    )

    response.raise_for_status()

    logging.info("API request successful")

    return response.json()


def save_raw_data(data: dict) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_file = RAW_DATA_DIR / f"weather_{timestamp}.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    logging.info("Raw data saved to %s", output_file)

    return output_file


def main() -> None:
    try:
        data = fetch_weather_data()

        output_file = save_raw_data(data)

        print(f"SUCCESS: Raw data saved to {output_file}")

    except requests.RequestException as exc:
        logging.exception("API request failed")

        print(f"ERROR: {exc}")


if __name__ == "__main__":
    main()