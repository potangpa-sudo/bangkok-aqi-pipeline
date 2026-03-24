from __future__ import annotations

import pendulum

from airflow import DAG
from airflow.exceptions import AirflowFailException
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from bangkok_aqi.alerts import notify_airflow_failure
from bangkok_aqi.extract import AQIPayloadValidationError, run_extract


def extract_raw_aqi_task() -> str:
    try:
        return run_extract()
    except AQIPayloadValidationError as exc:
        raise AirflowFailException(f"AQI extract validation failed: {exc}") from exc


with DAG(
    dag_id="bangkok_aqi_pipeline",
    description="Extract Bangkok AQI data and build the DuckDB warehouse with dbt.",
    start_date=pendulum.datetime(2024, 1, 1, tz="Asia/Bangkok"),
    schedule="0 * * * *",
    catchup=False,
    max_active_runs=1,
    tags=["portfolio", "aqi", "dbt"],
) as dag:
    extract_raw_aqi = PythonOperator(
        task_id="extract_raw_aqi",
        python_callable=extract_raw_aqi_task,
        on_failure_callback=notify_airflow_failure,
    )

    build_dbt_models = BashOperator(
        task_id="build_dbt_models",
        bash_command=(
            "set -euo pipefail && "
            "cd /opt/airflow/project && "
            "dbt build --project-dir dbt --profiles-dir dbt"
        ),
        on_failure_callback=notify_airflow_failure,
    )

    extract_raw_aqi >> build_dbt_models
