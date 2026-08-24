from pathlib import Path
import json
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_latest_raw_file() -> Path:
    files = list(RAW_DATA_DIR.glob("weather_*.json"))

    if not files:
        raise FileNotFoundError("No raw weather files found.")

    latest_file = max(files, key=lambda file: file.stat().st_mtime)

    return latest_file


def load_raw_data(file_path: Path) -> dict:
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def transform_weather_data(data: dict) -> pd.DataFrame:
    hourly = data["hourly"]

    dataframe = pd.DataFrame(
        {
            "timestamp": hourly["time"],
            "temperature_2m": hourly["temperature_2m"],
            "relative_humidity_2m": hourly["relative_humidity_2m"],
            "precipitation": hourly["precipitation"],
        }
    )

    dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"])

    dataframe = dataframe.drop_duplicates()

    dataframe = dataframe.dropna(
        subset=[
            "timestamp",
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
        ]
    )

    dataframe = dataframe.sort_values("timestamp")

    return dataframe


def save_processed_data(dataframe: pd.DataFrame) -> Path:
    output_file = PROCESSED_DATA_DIR / "weather_cleaned.csv"

    dataframe.to_csv(output_file, index=False)

    return output_file


def main() -> None:
    raw_file = get_latest_raw_file()

    print(f"Loading: {raw_file}")

    data = load_raw_data(raw_file)

    dataframe = transform_weather_data(data)

    output_file = save_processed_data(dataframe)

    print(f"Rows processed: {len(dataframe)}")
    print(f"SUCCESS: Cleaned data saved to {output_file}")


if __name__ == "__main__":
    main()