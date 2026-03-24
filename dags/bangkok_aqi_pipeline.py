from __future__ import annotations

import pendulum

from airflow import DAG
from airflow.exceptions import AirflowFailException
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from bangkok_aqi.alerts import notify_airflow_failure
from bangkok_aqi.extract import (
    AQIPayloadValidationError,
    extract_aqi_to_bronze,
    extract_weather_to_bronze,
)


def extract_raw_aqi_json_task() -> str:
    try:
        return extract_aqi_to_bronze()
    except AQIPayloadValidationError as exc:
        raise AirflowFailException(f"AQI extract validation failed: {exc}") from exc


def extract_raw_weather_json_task() -> str:
    try:
        return extract_weather_to_bronze()
    except AQIPayloadValidationError as exc:
        raise AirflowFailException(f"Weather extract validation failed: {exc}") from exc


with DAG(
    dag_id="bangkok_aqi_pipeline",
    description="Extract Bangkok AQI data and build the DuckDB warehouse with dbt.",
    start_date=pendulum.datetime(2024, 1, 1, tz="Asia/Bangkok"),
    schedule="0 * * * *",
    catchup=False,
    max_active_runs=1,
    tags=["portfolio", "aqi", "dbt"],
) as dag:
    extract_raw_aqi_json = PythonOperator(
        task_id="extract_raw_aqi_json",
        python_callable=extract_raw_aqi_json_task,
        retries=2,
        retry_delay=pendulum.duration(minutes=5),
        on_failure_callback=notify_airflow_failure,
    )

    extract_raw_weather_json = PythonOperator(
        task_id="extract_raw_weather_json",
        python_callable=extract_raw_weather_json_task,
        retries=2,
        retry_delay=pendulum.duration(minutes=5),
        on_failure_callback=notify_airflow_failure,
    )

    build_silver_models = BashOperator(
        task_id="build_silver_models",
        bash_command=(
            "set -euo pipefail && "
            "cd /opt/airflow/project && "
            "dbt build --project-dir dbt --profiles-dir dbt "
            "--select "
            "base_aqi_hourly_exploded "
            "base_weather_hourly_exploded "
            "stg_aqi_hourly "
            "stg_weather_hourly"
        ),
        on_failure_callback=notify_airflow_failure,
    )

    build_gold_mart = BashOperator(
        task_id="build_gold_mart",
        bash_command=(
            "set -euo pipefail && "
            "cd /opt/airflow/project && "
            "dbt build --project-dir dbt --profiles-dir dbt --select fct_aqi_hourly"
        ),
        on_failure_callback=notify_airflow_failure,
    )

    extract_raw_aqi_json >> build_silver_models
    extract_raw_weather_json >> build_silver_models
    build_silver_models >> build_gold_mart
