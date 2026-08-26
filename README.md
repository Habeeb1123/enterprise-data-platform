# Enterprise Data Platform

An end-to-end, production-style data engineering and analytics platform that ingests hourly weather data from an external API, transforms and validates the data, loads it idempotently into PostgreSQL, creates an SQL analytics layer, orchestrates workflows with Apache Airflow, monitors pipeline execution, validates changes through automated testing and CI/CD, and exposes analytical results through an interactive Power BI dashboard.

The project demonstrates practical data engineering concepts including API ingestion, ETL pipeline development, data transformation, PostgreSQL, SQL analytics, automated data-quality testing, Docker, Apache Airflow, GitHub Actions CI/CD, pipeline monitoring, structured logging, Git version control, and business intelligence reporting.

---

## Architecture

```text
External Weather API
        |
        v
Python API Ingestion
        |
        v
Raw JSON Data
        |
        v
Data Transformation & Validation
        |
        v
Cleaned Weather Dataset
        |
        v
PostgreSQL
        |
        +-------------------------+
        |                         |
        v                         v
Analytics SQL Views       Data Quality Tests
        |                         |
        v                         |
Power BI Dashboard                |
                                  |
        +-------------------------+
        |
        v
Pipeline Monitoring

Orchestration: Apache Airflow
Infrastructure: Docker Compose
CI/CD: GitHub Actions
```

The platform separates ingestion, transformation, storage, analytics, testing, monitoring, orchestration, visualisation, and continuous integration into distinct components.

---

## Technology Stack

### Data Engineering

- Python 3
- pandas
- requests
- SQLAlchemy
- psycopg2
- python-dotenv

### Database & Analytics

- PostgreSQL 17
- SQL
- PostgreSQL views

### Data Quality & Testing

- pytest
- Automated ingestion tests
- Automated database tests

### Infrastructure & Orchestration

- Docker
- Docker Compose
- Apache Airflow

### CI/CD

- GitHub Actions
- Automated test execution

### Monitoring & Logging

- Python logging
- Pipeline run-status tracking
- Pipeline health reporting
- JSONL execution history

### Business Intelligence

- Microsoft Power BI Desktop

### Development & Version Control

- Git
- GitHub
- Visual Studio Code

---

## Project Structure

```text
enterprise-data-platform/
|
|-- .github/
|   `-- workflows/
|       `-- ci.yml
|
|-- dags/
|   `-- weather_pipeline_dag.py
|
|-- data/
|   |-- raw/
|   `-- processed/
|
|-- logs/
|   `-- pipeline_runs.jsonl
|
|-- powerbi/
|   `-- weather_analytics_dashboard.pbix
|
|-- sql/
|   |-- create_weather_analytics_views.sql
|   |-- create_weather_table.sql
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
|   |-- monitoring/
|   |   |-- health_report.py
|   |   `-- pipeline_monitor.py
|   |
|   |-- transformation/
|   |   `-- clean_data.py
|   |
|   `-- logging_config.py
|
|-- tests/
|   |-- test_database.py
|   `-- test_ingestion.py
|
|-- .dockerignore
|-- .env.example
|-- .gitignore
|-- Dockerfile
|-- Dockerfile.airflow
|-- docker-compose.yml
|-- requirements.txt
|-- run_pipeline.py
`-- README.md
```

Generated raw and processed datasets, runtime logs, local environment variables, Python caches, and test caches are excluded from version control.

---

## Pipeline Workflow

The complete pipeline follows the following sequence:

```text
1. API Ingestion
       |
       v
2. Raw Data Persistence
       |
       v
3. Data Transformation & Validation
       |
       v
4. PostgreSQL Upsert
       |
       v
5. Analytics View Creation
       |
       v
6. Automated Data Quality Tests
       |
       v
7. Pipeline Run Monitoring
       |
       v
8. Power BI Analytics
```

Apache Airflow provides workflow orchestration, while GitHub Actions provides automated CI validation for repository changes.

---

## 1. API Data Ingestion

The ingestion component retrieves hourly weather observations from an external weather API.

The ingestion module is located at:

```text
src/ingestion/api_ingestion.py
```

Each successful API response is stored as a timestamped JSON file under:

```text
data/raw/
```

Persisting the original API response provides a raw-data layer and allows transformations to be reproduced independently from the external API.

---

## 2. Data Transformation

The transformation component is located at:

```text
src/transformation/clean_data.py
```

It selects the latest raw weather file, extracts hourly observations, validates the source structure, and converts the data into a clean tabular dataset.

The transformed dataset contains:

```text
timestamp
temperature_2m
relative_humidity_2m
precipitation
```

The cleaned dataset is written to:

```text
data/processed/weather_cleaned.csv
```

Transformation and quality checks cover:

- valid timestamps
- required columns
- null values
- duplicate timestamps
- numeric weather measurements
- valid humidity ranges
- non-negative precipitation
- reasonable temperature ranges

---

## 3. PostgreSQL Storage

The transformed weather data is loaded into PostgreSQL using:

```text
src/database/load_postgres.py
```

Database:

```text
datacareer_db
```

Primary weather table:

```text
public.weather_hourly
```

The table stores hourly observations including:

```text
timestamp
temperature_2m
relative_humidity_2m
precipitation
```

Database credentials are loaded from environment variables rather than being hard-coded into source code.

---

## Idempotent Database Loading

The PostgreSQL load uses an upsert strategy based on the weather timestamp.

Conceptually:

```sql
INSERT INTO weather_hourly (...)
VALUES (...)
ON CONFLICT (timestamp)
DO UPDATE SET ...;
```

This makes repeated pipeline execution idempotent.

Running the pipeline multiple times does not create duplicate observations for an existing timestamp. Existing records can instead be updated with the latest source values.

---

## SQL Analytics Layer

The project includes a dedicated analytics layer built using PostgreSQL views.

Analytics view definitions are stored in:

```text
sql/create_weather_analytics_views.sql
```

The platform creates three analytical views:

```text
public.weather_daily_summary
public.weather_hourly_enriched
public.weather_overall_kpis
```

### weather_daily_summary

Provides daily aggregations including:

- average temperature
- minimum temperature
- maximum temperature
- average humidity
- minimum humidity
- maximum humidity
- total precipitation
- hourly observation count

### weather_overall_kpis

Provides high-level metrics including:

- total observations
- total days
- earliest timestamp
- latest timestamp
- average temperature
- minimum temperature
- maximum temperature
- average humidity
- total precipitation

### weather_hourly_enriched

Extends the hourly dataset with analytical attributes including:

- weather date
- hour of day
- temperature category
- precipitation category

Temperature observations can be categorised into:

```text
Cold
Cool
Mild
Warm
```

Precipitation observations can be categorised into:

```text
Dry
Light Rain
Moderate Rain
Heavy Rain
```

---

## Automatic Analytics View Creation

Analytics views are automatically created or refreshed after the PostgreSQL data load.

```text
Weather Data Upsert
        |
        v
Analytics View Creation
```

This ensures that the analytical layer remains available after pipeline execution without requiring a separate manual SQL step.

---

## Automated Data Quality Testing

The project uses `pytest` for automated validation.

The current test suite contains:

```text
26 tests
```

### Ingestion and Transformation Tests

Tests validate:

- raw weather file existence
- hourly API data existence
- equal-length hourly arrays
- processed file existence
- non-empty processed data
- expected schema
- absence of null values
- valid timestamps
- unique timestamps
- sorted timestamps
- numeric temperature values
- reasonable temperature ranges
- numeric humidity values
- valid humidity ranges
- numeric precipitation values
- non-negative precipitation
- expected minimum dataset size

### Database Tests

Database tests validate:

- PostgreSQL connectivity
- weather table existence
- non-empty weather table
- duplicate timestamp prevention
- absence of null values
- valid humidity ranges
- non-negative precipitation
- reasonable temperature ranges
- expected database timestamp range

Run the complete test suite with:

```powershell
python -m pytest tests -v
```

A successful test run reports:

```text
26 passed
```

---

## Complete Pipeline Execution

The complete workflow can be executed from the project root with:

```powershell
python run_pipeline.py
```

The pipeline performs:

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
Analytics View Creation
      |
      v
Automated Tests
```

A successful execution ends with:

```text
PIPELINE COMPLETED SUCCESSFULLY
```

---

## Pipeline Monitoring

Pipeline execution is monitored using:

```text
src/monitoring/pipeline_monitor.py
```

Pipeline run metadata is recorded locally in:

```text
logs/pipeline_runs.jsonl
```

Execution metadata can include:

- execution status
- start timestamp
- finish timestamp
- execution duration
- failed pipeline step
- process exit code

Example:

```json
{
  "status": "success",
  "started_at": "2026-08-25T21:46:01+00:00",
  "finished_at": "2026-08-25T21:46:05+00:00",
  "duration_seconds": 3.828,
  "failed_step": null,
  "exit_code": 0
}
```

This provides lightweight operational observability and historical pipeline-run tracking.

---

## Pipeline Health Reporting

A health-reporting utility is available at:

```text
src/monitoring/health_report.py
```

Run it with:

```powershell
python -m src.monitoring.health_report
```

The report summarises operational metrics including:

- total pipeline runs
- successful runs
- failed runs
- pipeline success rate
- average execution duration
- latest pipeline status
- last successful execution
- last failed execution
- most recent failed step

---

## Docker Infrastructure

The project uses Docker Compose to provide containerised infrastructure.

The environment includes services for:

```text
PostgreSQL
Apache Airflow API Server
Apache Airflow Scheduler
Apache Airflow DAG Processor
```

PostgreSQL includes a health check to verify database availability.

Start the environment:

```powershell
docker compose up -d
```

Check running containers:

```powershell
docker compose ps
```

Stop the environment:

```powershell
docker compose down
```

---

## Apache Airflow Orchestration

Apache Airflow provides the workflow orchestration layer.

The Airflow environment runs through Docker Compose and provides:

- workflow scheduling
- task dependency management
- task execution
- operational visibility
- pipeline run history

The project includes the Airflow DAG:

```text
dags/weather_pipeline_dag.py
```

When the local Docker environment is running, the Airflow web interface is exposed through the configured Docker port.

---

## GitHub Actions CI/CD

Continuous integration is implemented using:

```text
.github/workflows/ci.yml
```

GitHub Actions automatically validates repository changes by running the project's automated test workflow.

The CI pipeline provides:

- automated validation of repository changes
- repeatable test execution
- PostgreSQL-backed integration testing
- early detection of pipeline regressions
- visible pass/fail status on GitHub

The current workflow is passing successfully.

---

## Power BI Analytics Dashboard

The project includes an interactive Microsoft Power BI dashboard located at:

```text
powerbi/weather_analytics_dashboard.pbix
```

The dashboard connects to the PostgreSQL analytics layer rather than relying directly on raw API files.

### Dashboard KPIs

The report includes KPI cards for:

- Total Observations
- Average Temperature
- Average Humidity
- Total Precipitation

### Analytical Visuals

The dashboard includes:

- Daily Temperature Trend
- Daily Precipitation
- Daily Average Humidity
- Temperature Category Distribution
- Precipitation Category Distribution
- Interactive Date Range filtering

The temperature trend compares:

- average temperature
- minimum temperature
- maximum temperature

The category visualisations provide a breakdown of weather conditions across hourly observations.

---

## Example Analytics

A representative dataset contained:

```text
192 hourly observations
8 days of weather data
Average temperature: 16.58 °C
Minimum temperature: 11.8 °C
Maximum temperature: 21.6 °C
Average relative humidity: 79.92%
Total precipitation: 22.60 mm
```

These metrics are exposed through PostgreSQL analytics views and the Power BI dashboard.

---

## Logging and Error Handling

The pipeline uses structured Python logging across the main components.

Logging captures events including:

- API request execution
- successful API responses
- raw-data persistence
- transformation execution
- PostgreSQL loading
- analytics view creation
- automated testing
- pipeline completion
- pipeline failures

Exceptions are logged and re-raised where appropriate so failures remain visible to developers and orchestration systems.

---

## Environment Configuration

Sensitive configuration is stored locally in:

```text
.env
```

The repository provides a safe configuration template:

```text
.env.example
```

Create your local environment configuration by copying the template and replacing the placeholder values.

Required variables include:

```text
DB_HOST=localhost
DB_PORT=5433
DB_NAME=datacareer_db
DB_USER=datacareer_user
DB_PASSWORD=change_me
DB_PASSWORD_URLENC=change_me
AIRFLOW_JWT_SECRET=change_me_to_a_long_random_secret
```

`DB_PASSWORD_URLENC` should contain the URL-encoded version of the database password when special characters are present.

The real `.env` file is excluded by `.gitignore` and must never be committed to GitHub.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Habeeb1123/enterprise-data-platform.git
cd enterprise-data-platform
```

Create a Python virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Install the required dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create the local environment file from `.env.example` and replace its placeholder values with your local configuration.

Start the Docker infrastructure:

```powershell
docker compose up -d
```

Verify the containers:

```powershell
docker compose ps
```

Run the pipeline:

```powershell
python run_pipeline.py
```

---

## Useful Commands

### Run the complete pipeline

```powershell
python run_pipeline.py
```

### Run automated tests

```powershell
python -m pytest tests -v
```

### Generate the pipeline health report

```powershell
python -m src.monitoring.health_report
```

### Start Docker services

```powershell
docker compose up -d
```

### Check Docker services

```powershell
docker compose ps
```

### Stop Docker services

```powershell
docker compose down
```

### Query PostgreSQL

```powershell
docker compose exec postgres psql -U datacareer_user -d datacareer_db
```

### Check repository status

```powershell
git status
```

---

## Security and Repository Hygiene

The repository follows several basic security and source-control practices:

- real environment credentials are excluded from Git
- `.env` is ignored
- `.env.example` contains placeholder configuration only
- database passwords are supplied through environment variables
- Airflow authentication secrets are supplied through environment variables
- generated raw data is ignored
- generated processed data is ignored
- runtime logs are ignored
- Python caches are ignored
- pytest caches are ignored

No production or personal credentials should be committed to this repository.

---

## Engineering Concepts Demonstrated

This project demonstrates practical experience with:

- end-to-end ETL pipeline design
- REST API ingestion
- raw-data persistence
- data cleaning and transformation
- PostgreSQL database engineering
- idempotent upserts
- SQL analytical modelling
- reusable SQL views
- automated data-quality testing
- integration testing
- Docker containerisation
- Docker Compose
- Apache Airflow orchestration
- GitHub Actions CI/CD
- structured logging
- pipeline monitoring
- operational health reporting
- Power BI analytics
- environment-based configuration
- Git and GitHub workflows
- modular Python project design

---

## Current Status

Implemented:

- [x] External API ingestion
- [x] Timestamped raw-data persistence
- [x] Data transformation
- [x] Data validation
- [x] PostgreSQL integration
- [x] Idempotent database upserts
- [x] SQL analytics
- [x] Analytical PostgreSQL views
- [x] Automatic analytics-view creation
- [x] Automated ingestion tests
- [x] Automated database tests
- [x] Complete pipeline runner
- [x] Structured logging
- [x] Pipeline run monitoring
- [x] Pipeline health reporting
- [x] Docker Compose infrastructure
- [x] Apache Airflow orchestration
- [x] GitHub Actions CI/CD
- [x] Power BI analytics dashboard
- [x] Interactive dashboard date filtering
- [x] Environment configuration template
- [x] Git/GitHub version control

---

## Potential Future Improvements

Possible extensions include:

1. Cloud deployment
2. Cloud object storage for the raw-data layer
3. Managed PostgreSQL or cloud data warehouse integration
4. Automated Power BI refresh
5. Alerting for failed pipeline runs
6. Historical weather ingestion across larger time ranges
7. Additional Airflow workflow monitoring
8. Data lineage and metadata tracking
9. Infrastructure as Code

These are optional extensions rather than requirements for the current local portfolio implementation.

---

## Author

Habeeb Ali Mumtaz