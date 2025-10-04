# Bangkok AQI Pipeline

Bring Bangkok's hourly weather and air-quality data together with DuckDB transforms and a Streamlit dashboard. The project is intentionally compact so you can run it locally today while still demonstrating end-to-end data engineering skills.

## Project Structure

```
bangkok-aqi-pipeline/
├─ data/
│  ├─ raw/                     # persisted API payloads
│  ├─ screenshots/             # drop Streamlit captures here
│  └─ warehouse.duckdb         # created at runtime
├─ sql/                        # ordered transformation models
├─ src/                        # ingestion, loading, testing, orchestration
└─ app/dashboard.py            # Streamlit UI
```

### Data Flow Highlights

1. `src.pipeline` calls the Open-Meteo weather and air-quality endpoints for Bangkok.
2. Raw JSON is stored under `data/raw/` and normalized with pandas.
3. Clean frames are upserted into DuckDB `raw.*` tables.
4. SQL models build hourly staging, a datetime dimension, an hourly fact, and the daily mart table.
5. `app/dashboard.py` surfaces daily KPIs and trend charts straight from DuckDB.

## Getting Started

1. Clone or copy the repository to your machine.
2. (Optional) create a virtual environment.
3. Run `make setup` to install dependencies and create data folders.
4. Copy `.env.example` to `.env` if you want to override defaults (lat/lon, bootstrap window).
5. Execute `make run` to ingest data and build the mart.
6. Inspect data quality with `make test`.
7. Launch the dashboard via `make dashboard`.

### Core Make Targets

- `make setup` – install dependencies and prepare folders.
- `make run` – full ingestion + transformation run (`python -m src.pipeline`).
- `make transform` – re-run only the SQL models against existing raw tables.
- `make test` – lightweight data quality assertions.
- `make dashboard` – start Streamlit in headless mode.
- `make all` – setup, run, and test in sequence.

### Configuration

Environment variables (loaded from `.env` when present):

- `LAT` / `LON` – coordinates for Bangkok (defaults provided).
- `BOOTSTRAP_HOURS` – number of trailing hours to retain when ingesting (default `72`).
- `TIMEZONE` – timezone passed to Open-Meteo (default `Asia/Bangkok`).

## Data Model

ASCII ERD of the DuckDB structures:

```
+-------------------+        +-----------------------+
| raw.raw_weather   |        | raw.raw_air_quality   |
+-------------------+        +-----------------------+
            \                        /
             v                      v
      stg.stg_weather       stg.stg_air_quality
             \                      /
              v                    v
             stg.dim_datetime (hour grain)
                       |
                       v
              fct.aqi_by_hour (hour grain)
                       |
                       v
           mart.daily_aqi_weather (day grain)
```

`mart.daily_aqi_weather` exposes daily averages for PM2.5, temperature, humidity, precipitation, wind, plus a simple PM2.5-based AQI proxy (rounded `pm2_5 * 4`).

## Testing

`make test` validates:

- Required tables exist (`raw.raw_weather`, `raw.raw_air_quality`, `mart.daily_aqi_weather`).
- Each table contains rows.
- The mart has data within the last three days.

## Streamlit Dashboard

The dashboard displays:

- KPI cards for latest daily PM2.5, temperature, and humidity.
- A line chart tracking PM2.5 and temperature over time.
- A bar chart showing the PM2.5 proxy AQI.
- The trailing daily observations table.

Data is read-only; the app never calls external APIs.

## Next Steps

- Implement the official Thailand AQI formula (with pollutant breakpoints and category branding).
- Package the project with Docker for reproducible execution environments.
- Migrate orchestration to Airflow or Prefect and schedule ingestion.
- Swap SQL handoffs for dbt models with tests and documentation.

## What This Demonstrates to Recruiters

- Ability to design and implement an end-to-end data pipeline with clear layering.
- Comfort combining Python ingestion, SQL transformations, and lightweight orchestration.
- Pragmatic data quality testing embedded alongside the pipeline.
- Skill presenting insights through a polished Streamlit dashboard tied to the warehouse.
- Familiarity with modern tooling (DuckDB, pandas, Makefile automation, environment-driven config).

Happy hacking!
