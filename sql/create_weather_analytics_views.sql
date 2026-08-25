CREATE OR REPLACE VIEW public.weather_daily_summary AS
SELECT
    DATE(timestamp) AS weather_date,
    ROUND(AVG(temperature_2m)::numeric, 2) AS avg_temperature_2m,
    MIN(temperature_2m) AS min_temperature_2m,
    MAX(temperature_2m) AS max_temperature_2m,
    ROUND(AVG(relative_humidity_2m)::numeric, 2) AS avg_relative_humidity_2m,
    MIN(relative_humidity_2m) AS min_relative_humidity_2m,
    MAX(relative_humidity_2m) AS max_relative_humidity_2m,
    ROUND(SUM(precipitation)::numeric, 2) AS total_precipitation,
    COUNT(*) AS hourly_observations
FROM public.weather_hourly
GROUP BY DATE(timestamp)
ORDER BY weather_date;


CREATE OR REPLACE VIEW public.weather_overall_kpis AS
SELECT
    COUNT(*) AS total_observations,
    COUNT(DISTINCT DATE(timestamp)) AS total_days,
    MIN(timestamp) AS earliest_timestamp,
    MAX(timestamp) AS latest_timestamp,
    ROUND(AVG(temperature_2m)::numeric, 2) AS avg_temperature_2m,
    MIN(temperature_2m) AS min_temperature_2m,
    MAX(temperature_2m) AS max_temperature_2m,
    ROUND(AVG(relative_humidity_2m)::numeric, 2) AS avg_relative_humidity_2m,
    ROUND(SUM(precipitation)::numeric, 2) AS total_precipitation
FROM public.weather_hourly;


CREATE OR REPLACE VIEW public.weather_hourly_enriched AS
SELECT
    timestamp,
    DATE(timestamp) AS weather_date,
    EXTRACT(HOUR FROM timestamp)::integer AS weather_hour,
    temperature_2m,
    relative_humidity_2m,
    precipitation,
    CASE
        WHEN temperature_2m < 5 THEN 'Cold'
        WHEN temperature_2m < 15 THEN 'Cool'
        WHEN temperature_2m < 25 THEN 'Mild'
        ELSE 'Warm'
    END AS temperature_category,
    CASE
        WHEN precipitation = 0 THEN 'Dry'
        WHEN precipitation < 2.5 THEN 'Light Rain'
        WHEN precipitation < 7.5 THEN 'Moderate Rain'
        ELSE 'Heavy Rain'
    END AS precipitation_category
FROM public.weather_hourly;