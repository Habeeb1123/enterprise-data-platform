# Enterprise Data Platform

An end-to-end data engineering project that ingests weather data from an external API, transforms and validates the data, loads it into PostgreSQL, and provides SQL-based analytics.

The project demonstrates a practical ETL pipeline using Python, PostgreSQL, SQLAlchemy, automated testing, and a modular project structure.

## Architecture

```text
Weather API
    |
    v
Python API Ingestion
    |
    v
Raw JSON Data
    |
    v
Data Transformation
    |
    v
Cleaned CSV
    |
    v
PostgreSQL
    |
    v
SQL Analytics
```

Automated tests validate the pipeline and processed data.

## Technology Stack

- Python 3
- PostgreSQL
- SQL
- SQLAlchemy
- psycopg2
- pandas
- requests
- python-dotenv
- pytest
- Git
- GitHub

## Project Structure

```text
enterprise-data-platform/
|
|-- data/
|   |-- raw/
|   `-- processed/
|
|-- sql/
|   `-- weather_analytics.sql
|
|-- src/
|   |-- database/
|   |   |-- connection.py
|   |   `-- load_postgres.py
|   |
|   |-- ingestion/
|   |   `-- api_ingestion.py
|   |
|   `-- transformation/
|       `-- clean_data.py
|
|-- tests/
|   `-- test_ingestion.py
|
|-- .env
|-- .gitignore
|-- requirements.txt
|-- run_pipeline.py
`-- README.md
```

## Pipeline Workflow

### 1. Data Ingestion

`src/ingestion/api_ingestion.py` retrieves hourly weather data from the weather API.

Each API response is stored as a timestamped JSON file in:

```text
data/raw/
```

This preserves the original source data before transformation.

### 2. Data Transformation

`src/transformation/clean_data.py` loads the latest raw JSON file and transforms the hourly weather observations into a structured dataset.

The processed dataset contains:

- timestamp
- temperature_2m
- relative_humidity_2m
- precipitation

The cleaned data is written to:

```text
data/processed/weather_cleaned.csv
```

A successful pipeline run currently processes 168 hourly observations.

### 3. PostgreSQL Load

`src/database/load_postgres.py` loads the transformed dataset into PostgreSQL.

Database:

```text
datacareer_db
```

Table:

```text
weather_hourly
```

The table contains the cleaned hourly weather observations used by the analytics layer.

Database credentials are loaded from environment variables rather than hard-coded into the Python source code.

## SQL Analytics

The project contains an analytics layer in:

```text
sql/weather_analytics.sql
```

The SQL queries calculate:

- average, minimum, and maximum temperature
- average, minimum, and maximum humidity
- total precipitation
- daily weather summaries
- highest-temperature periods
- highest-precipitation periods
- highest-humidity periods

Example results from a seven-day dataset:

```text
Average temperature: 16.10
Minimum temperature: 11.2
Maximum temperature: 18.7

Average humidity: 81.96
Minimum humidity: 57
Maximum humidity: 99

Total precipitation: 28.80
```

The daily aggregation identified 27 August 2026 as the wettest day in the dataset, with total precipitation of `21.20`.

## Automated Data Quality Testing

The project uses `pytest` to validate the pipeline output.

Current tests verify:

- raw weather data exists
- raw API data contains hourly observations
- processed data exists
- processed data is not empty
- required columns are present
- processed data contains no null values
- humidity values remain within a valid range
- precipitation values are non-negative

Current test result:

```text
8 passed
```

Run the test suite with:

```powershell
python -m pytest -v
```

## Running the Complete Pipeline

The complete workflow can be executed from the project root with:

```powershell
python run_pipeline.py
```

The pipeline automatically performs:

```text
API Ingestion
      |
      v
Data Transformation
      |
      v
PostgreSQL Load
      |
      v
Automated Tests
```

A successful execution ends with:

```text
PIPELINE COMPLETED SUCCESSFULLY
```

## Installation

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd enterprise-data-platform
```

Create and activate a Python virtual environment.

Install the required dependencies:

```bash
python -m pip install -r requirements.txt
```

PostgreSQL must also be installed and running.

## Environment Configuration

Database credentials should be stored in a local `.env` file.

Example structure:

```text
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
```

The `.env` file must not be committed to GitHub.

## Current Status

The project currently supports:

- API data ingestion
- raw data persistence
- data transformation
- PostgreSQL integration
- SQL analytics
- automated data-quality testing
- one-command pipeline execution

## Planned Improvements

Future development will add:

1. Production-style logging and error handling
2. Idempotent database loading and stronger database constraints
3. Docker containerisation
4. Pipeline orchestration and scheduling
5. Power BI analytics dashboard
6. CI/CD using GitHub Actions

These improvements will evolve the project from a local ETL pipeline into a more production-oriented data platform.

## Author

Habeeb Ali Mumtaz