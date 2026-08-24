-- Weather Analytics
-- Source table: weather_hourly


-- 1. Overall temperature summary
SELECT
    ROUND(AVG(temperature_2m)::numeric, 2) AS avg_temperature,
    MIN(temperature_2m) AS min_temperature,
    MAX(temperature_2m) AS max_temperature
FROM weather_hourly;


-- 2. Overall humidity summary
SELECT
    ROUND(AVG(relative_humidity_2m)::numeric, 2) AS avg_humidity,
    MIN(relative_humidity_2m) AS min_humidity,
    MAX(relative_humidity_2m) AS max_humidity
FROM weather_hourly;


-- 3. Total precipitation
SELECT
    ROUND(SUM(precipitation)::numeric, 2) AS total_precipitation
FROM weather_hourly;


-- 4. Daily weather summary
SELECT
    DATE(timestamp) AS weather_date,
    ROUND(AVG(temperature_2m)::numeric, 2) AS avg_temperature,
    MIN(temperature_2m) AS min_temperature,
    MAX(temperature_2m) AS max_temperature,
    ROUND(AVG(relative_humidity_2m)::numeric, 2) AS avg_humidity,
    ROUND(SUM(precipitation)::numeric, 2) AS total_precipitation
FROM weather_hourly
GROUP BY DATE(timestamp)
ORDER BY weather_date;


-- 5. Hottest 10 hours
SELECT
    timestamp,
    temperature_2m
FROM weather_hourly
ORDER BY temperature_2m DESC
LIMIT 10;


-- 6. Wettest 10 hours
SELECT
    timestamp,
    precipitation
FROM weather_hourly
WHERE precipitation > 0
ORDER BY precipitation DESC
LIMIT 10;


-- 7. Highest humidity hours
SELECT
    timestamp,
    relative_humidity_2m
FROM weather_hourly
ORDER BY relative_humidity_2m DESC
LIMIT 10;