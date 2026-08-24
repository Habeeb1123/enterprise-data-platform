from pathlib import Path

import pandas as pd
from sqlalchemy import BigInteger, DateTime, Float

from connection import get_engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_FILE = PROJECT_ROOT / "data" / "processed" / "weather_cleaned.csv"


def load_weather_data() -> None:
    dataframe = pd.read_csv(
        PROCESSED_FILE,
        parse_dates=["timestamp"],
    )

    engine = get_engine()

    dataframe.to_sql(
        "weather_hourly",
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

    print(f"SUCCESS: Loaded {len(dataframe)} rows into weather_hourly")


if __name__ == "__main__":
    load_weather_data()