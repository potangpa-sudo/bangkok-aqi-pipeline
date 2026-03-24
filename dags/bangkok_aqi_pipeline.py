from __future__ import annotations

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator


with DAG(
    dag_id="bangkok_aqi_pipeline",
    description="Extract Bangkok AQI data and build the DuckDB warehouse with dbt.",
    start_date=pendulum.datetime(2024, 1, 1, tz="Asia/Bangkok"),
    schedule="0 * * * *",
    catchup=False,
    max_active_runs=1,
    tags=["portfolio", "aqi", "dbt"],
) as dag:
    extract_raw_aqi = BashOperator(
        task_id="extract_raw_aqi",
        bash_command="cd /opt/airflow/project && python -m bangkok_aqi.cli extract",
    )

    build_dbt_models = BashOperator(
        task_id="build_dbt_models",
        bash_command=(
            "cd /opt/airflow/project && "
            "dbt build --project-dir dbt --profiles-dir dbt"
        ),
    )

    extract_raw_aqi >> build_dbt_models
