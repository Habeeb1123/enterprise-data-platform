CREATE TABLE IF NOT EXISTS weather_hourly (
    timestamp TIMESTAMP PRIMARY KEY,
    temperature_2m DOUBLE PRECISION NOT NULL,
    relative_humidity_2m BIGINT NOT NULL
        CHECK (relative_humidity_2m BETWEEN 0 AND 100),
    precipitation DOUBLE PRECISION NOT NULL
        CHECK (precipitation >= 0)
);