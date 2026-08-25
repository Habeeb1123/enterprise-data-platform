from pathlib import Path
import json

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_FILE = PROJECT_ROOT / "data" / "processed" / "weather_cleaned.csv"

EXPECTED_COLUMNS = {
    "timestamp",
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
}


def load_processed_data():
    """Load the processed weather dataset."""
    return pd.read_csv(PROCESSED_FILE)


def get_latest_raw_file():
    """Return the most recently modified raw weather JSON file."""
    files = list(RAW_DATA_DIR.glob("weather_*.json"))

    assert len(files) > 0, "No raw weather JSON files were found."

    return max(files, key=lambda file: file.stat().st_mtime)


def test_raw_weather_file_exists():
    files = list(RAW_DATA_DIR.glob("weather_*.json"))

    assert len(files) > 0


def test_raw_weather_contains_hourly_data():
    latest_file = get_latest_raw_file()

    with latest_file.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert "hourly" in data
    assert "time" in data["hourly"]
    assert "temperature_2m" in data["hourly"]
    assert "relative_humidity_2m" in data["hourly"]
    assert "precipitation" in data["hourly"]


def test_raw_hourly_arrays_have_equal_length():
    latest_file = get_latest_raw_file()

    with latest_file.open("r", encoding="utf-8") as file:
        data = json.load(file)

    hourly = data["hourly"]

    lengths = {
        len(hourly["time"]),
        len(hourly["temperature_2m"]),
        len(hourly["relative_humidity_2m"]),
        len(hourly["precipitation"]),
    }

    assert len(lengths) == 1


def test_processed_file_exists():
    assert PROCESSED_FILE.exists()


def test_processed_data_not_empty():
    dataframe = load_processed_data()

    assert len(dataframe) > 0


def test_processed_data_has_expected_columns():
    dataframe = load_processed_data()

    assert EXPECTED_COLUMNS.issubset(dataframe.columns)


def test_no_null_values():
    dataframe = load_processed_data()

    assert dataframe[list(EXPECTED_COLUMNS)].isnull().sum().sum() == 0


def test_timestamp_values_are_valid():
    dataframe = load_processed_data()

    timestamps = pd.to_datetime(dataframe["timestamp"], errors="coerce")

    assert timestamps.notna().all()


def test_timestamps_are_unique():
    dataframe = load_processed_data()

    assert dataframe["timestamp"].is_unique


def test_timestamps_are_sorted():
    dataframe = load_processed_data()

    timestamps = pd.to_datetime(dataframe["timestamp"])

    assert timestamps.is_monotonic_increasing


def test_temperature_is_numeric():
    dataframe = load_processed_data()

    temperature = pd.to_numeric(
        dataframe["temperature_2m"],
        errors="coerce",
    )

    assert temperature.notna().all()


def test_temperature_reasonable_range():
    dataframe = load_processed_data()

    temperature = pd.to_numeric(
        dataframe["temperature_2m"],
        errors="coerce",
    )

    assert temperature.between(-90, 60).all()


def test_humidity_is_numeric():
    dataframe = load_processed_data()

    humidity = pd.to_numeric(
        dataframe["relative_humidity_2m"],
        errors="coerce",
    )

    assert humidity.notna().all()


def test_humidity_valid_range():
    dataframe = load_processed_data()

    humidity = pd.to_numeric(
        dataframe["relative_humidity_2m"],
        errors="coerce",
    )

    assert humidity.between(0, 100).all()


def test_precipitation_is_numeric():
    dataframe = load_processed_data()

    precipitation = pd.to_numeric(
        dataframe["precipitation"],
        errors="coerce",
    )

    assert precipitation.notna().all()


def test_precipitation_not_negative():
    dataframe = load_processed_data()

    precipitation = pd.to_numeric(
        dataframe["precipitation"],
        errors="coerce",
    )

    assert (precipitation >= 0).all()


def test_dataset_has_expected_minimum_size():
    dataframe = load_processed_data()

    assert len(dataframe) >= 24