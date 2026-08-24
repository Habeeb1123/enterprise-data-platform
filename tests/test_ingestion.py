from pathlib import Path
import json

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_FILE = PROJECT_ROOT / "data" / "processed" / "weather_cleaned.csv"


def test_raw_weather_file_exists():
    files = list(RAW_DATA_DIR.glob("weather_*.json"))
    assert len(files) > 0


def test_raw_weather_contains_hourly_data():
    files = list(RAW_DATA_DIR.glob("weather_*.json"))
    latest_file = max(files, key=lambda file: file.stat().st_mtime)

    with latest_file.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert "hourly" in data
    assert "time" in data["hourly"]
    assert "temperature_2m" in data["hourly"]
    assert "relative_humidity_2m" in data["hourly"]
    assert "precipitation" in data["hourly"]


def test_processed_file_exists():
    assert PROCESSED_FILE.exists()


def test_processed_data_not_empty():
    dataframe = pd.read_csv(PROCESSED_FILE)

    assert len(dataframe) > 0


def test_processed_data_has_expected_columns():
    dataframe = pd.read_csv(PROCESSED_FILE)

    expected_columns = {
        "timestamp",
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
    }

    assert expected_columns.issubset(dataframe.columns)


def test_no_null_values():
    dataframe = pd.read_csv(PROCESSED_FILE)

    assert dataframe.isnull().sum().sum() == 0


def test_humidity_valid_range():
    dataframe = pd.read_csv(PROCESSED_FILE)

    assert dataframe["relative_humidity_2m"].between(0, 100).all()


def test_precipitation_not_negative():
    dataframe = pd.read_csv(PROCESSED_FILE)

    assert (dataframe["precipitation"] >= 0).all()