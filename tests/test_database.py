import os

import psycopg2


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "datacareer_db")
DB_USER = os.getenv("DB_USER", "datacareer_user")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def test_database_connection():
    connection = get_connection()

    try:
        assert connection.closed == 0
    finally:
        connection.close()


def test_weather_table_exists():
    query = """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = 'weather_hourly'
        );
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            exists = cursor.fetchone()[0]

        assert exists is True
    finally:
        connection.close()


def test_weather_table_not_empty():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM public.weather_hourly;"
            )
            row_count = cursor.fetchone()[0]

        assert row_count > 0
    finally:
        connection.close()


def test_no_duplicate_timestamps():
    query = """
        SELECT COUNT(*)
        FROM (
            SELECT timestamp
            FROM public.weather_hourly
            GROUP BY timestamp
            HAVING COUNT(*) > 1
        ) duplicates;
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            duplicate_count = cursor.fetchone()[0]

        assert duplicate_count == 0
    finally:
        connection.close()


def test_no_null_values():
    query = """
        SELECT COUNT(*)
        FROM public.weather_hourly
        WHERE timestamp IS NULL
           OR temperature_2m IS NULL
           OR relative_humidity_2m IS NULL
           OR precipitation IS NULL;
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            null_count = cursor.fetchone()[0]

        assert null_count == 0
    finally:
        connection.close()


def test_humidity_valid_range():
    query = """
        SELECT COUNT(*)
        FROM public.weather_hourly
        WHERE relative_humidity_2m < 0
           OR relative_humidity_2m > 100;
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            invalid_count = cursor.fetchone()[0]

        assert invalid_count == 0
    finally:
        connection.close()


def test_precipitation_not_negative():
    query = """
        SELECT COUNT(*)
        FROM public.weather_hourly
        WHERE precipitation < 0;
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            invalid_count = cursor.fetchone()[0]

        assert invalid_count == 0
    finally:
        connection.close()


def test_temperature_reasonable_range():
    query = """
        SELECT COUNT(*)
        FROM public.weather_hourly
        WHERE temperature_2m < -80
           OR temperature_2m > 60;
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            invalid_count = cursor.fetchone()[0]

        assert invalid_count == 0
    finally:
        connection.close()


def test_database_timestamp_range():
    query = """
        SELECT
            COUNT(*) AS total_rows,
            MIN(timestamp) AS earliest,
            MAX(timestamp) AS latest
        FROM public.weather_hourly;
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            total_rows, earliest, latest = cursor.fetchone()

        assert total_rows > 0
        assert earliest is not None
        assert latest is not None
        assert earliest <= latest
    finally:
        connection.close()