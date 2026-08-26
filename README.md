# Enterprise Data Platform

An end-to-end, production-style data engineering and analytics platform that ingests hourly weather data from an external API, transforms and validates the data, loads it idempotently into PostgreSQL, creates an SQL analytics layer, monitors pipeline execution, orchestrates data workflows, and exposes analytical results through an interactive Power BI dashboard.

The project demonstrates practical data engineering concepts including API ingestion, ETL pipeline development, data transformation, PostgreSQL, SQL analytics, automated data-quality testing, Docker, Apache Airflow, pipeline monitoring, logging, Git version control, and business intelligence reporting.

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
        +----------------------+
        |                      |
        v                      v
Analytics SQL Views      Data Quality Tests
        |                      |
        v                      |
Power BI Dashboard             |
                               |
        +----------------------+
        |
        v
Pipeline Monitoring

Orchestration: Apache Airflow
Infrastructure: Docker Compose
```

The platform separates ingestion, transformation, storage, analytics, testing, monitoring, orchestration, and visualisation into distinct components.

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
|-- dags/
|   `-- ...
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
|   `-- weather_analytics.sql
|
|-- src/
|   |
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
|   `-- transformation/
|       `-- clean_data.py
|
|-- tests/
|   |-- test_database.py
|   `-- test_ingestion.py
|
|-- .env
|-- .gitignore
|-- docker-compose.yml
|-- requirements.txt
|-- run_pipeline.py
`-- README.md
```

Generated raw and processed datasets, local environment variables, logs, caches, and other runtime artifacts can be excluded from version control where appropriate.

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
3. Data Transformation
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

Example:

```text
weather_20260825_231023.json
```

Persisting the original API response provides a raw-data layer and allows transformations to be reproduced independently from the external API.

---

## 2. Data Transformation

The transformation component is located at:

```text
src/transformation/clean_data.py
```

It selects the latest raw weather file, extracts the hourly observations, validates the structure, and converts the source data into a clean tabular dataset.

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

Transformation logic includes checks for:

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

Database credentials are loaded from environment variables rather than being hard-coded into the source code.

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

Temperature observations are categorised into groups such as:

```text
Cold
Cool
Mild
Warm
```

Precipitation observations are categorised into groups such as:

```text
Dry
Light Rain
Moderate Rain
Heavy Rain
```

---

## Automatic Analytics View Creation

Analytics views are automatically created or refreshed after the PostgreSQL data load.

The database load therefore performs two related operations:

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

The test suite currently contains:

```text
26 tests
```

The tests cover both the file-based pipeline and PostgreSQL database layer.

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

The entire workflow can be executed from the project root using:

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

Pipeline run metadata is recorded in:

```text
logs/pipeline_runs.jsonl
```

Each execution record can include information such as:

- execution status
- start timestamp
- finish timestamp
- execution duration
- failed pipeline step
- process exit code

Example structure:

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

This adds an operational monitoring layer beyond standard application logging.

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

The PostgreSQL service includes a health check to verify database availability.

Check running containers with:

```powershell
docker compose ps
```

Start the environment with:

```powershell
docker compose up -d
```

Stop the environment with:

```powershell
docker compose down
```

---

## Apache Airflow Orchestration

Apache Airflow provides the orchestration layer for the project.

The Airflow environment runs through Docker Compose and includes the components required to schedule and manage data workflows.

Airflow provides capabilities such as:

- workflow scheduling
- dependency management
- task execution
- operational visibility
- pipeline run history

When the local environment is running, the Airflow web interface is exposed through the configured Docker port.

---

## Power BI Analytics Dashboard

The project includes an interactive Microsoft Power BI dashboard located at:

```text
powerbi/weather_analytics_dashboard.pbix
```

The dashboard connects to the PostgreSQL analytics layer rather than relying directly on raw API files.

### Dashboard KPIs

The report includes high-level KPI cards for:

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

The category visualisations provide an immediate breakdown of weather conditions across hourly observations.

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

These metrics are exposed through the PostgreSQL analytics views and Power BI dashboard.

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

Exceptions are logged and re-raised where appropriate so failures remain visible to both developers and orchestration systems.

---

## Environment Configuration

Sensitive database configuration is stored in a local `.env` file.

Example:

```text
DB_HOST=localhost
DB_PORT=5433
DB_NAME=datacareer_db
DB_USER=your_username
DB_PASSWORD=your_password
```

The `.env` file should never be committed to GitHub.

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd enterprise-data-platform
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create the local `.env` file with the required database configuration.

Start the Docker infrastructure:

```powershell
docker compose up -d
```

Verify the containers:

```powershell
docker compose ps
```

Then run the pipeline:

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

### Check Docker services

```powershell
docker compose ps
```

### Query PostgreSQL

```powershell
docker compose exec postgres psql -U datacareer_user -d datacareer_db
```

### Check Git repository status

```powershell
git status
```

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
- Docker containerisation
- Apache Airflow orchestration
- structured logging
- pipeline monitoring
- operational health reporting
- Power BI analytics
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
- [x] Apache Airflow environment
- [x] Power BI analytics dashboard
- [x] Interactive dashboard date filtering
- [x] Git/GitHub version control

---

## Potential Future Improvements

Possible extensions include:

1. GitHub Actions CI/CD
2. Cloud deployment
3. Cloud object storage for the raw-data layer
4. Managed PostgreSQL or cloud data warehouse integration
5. Automated Power BI refresh
6. Alerting for failed pipeline runs
7. Historical weather ingestion across larger time ranges
8. Additional Airflow workflow monitoring
9. Data lineage and metadata tracking
10. Infrastructure as Code

---

## Author

Habeeb Ali Mumtaz