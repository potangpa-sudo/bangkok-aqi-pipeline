"""
Airflow DAG for hourly Bangkok AQI data pipeline.

Schedule: Every hour at minute 0 (Asia/Bangkok timezone)
Steps:
1. Trigger Cloud Run ingestor service
2. Sensor: Wait for new data in GCS partition
3. Data quality gate: Validate raw data
4. Submit Dataproc Serverless Spark job for cleansing
5. Run dbt models (incremental staging + marts)
6. Notify on failure
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.google.cloud.operators.cloud_run import CloudRunExecuteJobOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectsWithPrefixExistenceSensor
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.utils.trigger_rule import TriggerRule

from google.cloud import storage

# Environment variables
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "your-project-id")
REGION = os.getenv("GCP_REGION", "asia-southeast1")
RAW_BUCKET = os.getenv("GCS_BUCKET_RAW", "bangkok-aqi-raw")
QUAR_BUCKET = os.getenv("GCS_BUCKET_QUAR", "bangkok-aqi-quarantine")
INGESTOR_URL = os.getenv("INGESTOR_SERVICE_URL", "https://aqi-ingestor-xxx.run.app")
DATAPROC_SA = os.getenv("DATAPROC_SERVICE_ACCOUNT", f"aqi-dataproc-sa@{PROJECT_ID}.iam.gserviceaccount.com")
SLACK_WEBHOOK_CONN = os.getenv("SLACK_WEBHOOK_CONN", "slack_webhook")

# Default args for all tasks
default_args = {
    "owner": "data-eng",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=30),
}

# DAG definition
dag = DAG(
    dag_id="aqi_hourly_pipeline",
    default_args=default_args,
    description="Hourly Bangkok AQI data ingestion and processing",
    schedule_interval="0 * * * *",  # Every hour at minute 0
    start_date=datetime(2025, 10, 1, tzinfo="Asia/Bangkok"),
    catchup=False,
    max_active_runs=1,
    tags=["aqi", "hourly", "production"],
)


def get_partition_prefix(**context) -> str:
    """Generate GCS partition prefix for current execution date."""
    execution_date = context["execution_date"]
    date_str = execution_date.strftime("%Y-%m-%d")
    hour_str = execution_date.strftime("%H")
    return f"date={date_str}/hour={hour_str}/"


def validate_raw_data(**context) -> str:
    """
    Validate raw data quality before processing.
    Returns task_id to branch to.
    """
    prefix = get_partition_prefix(**context)
    
    client = storage.Client()
    bucket = client.bucket(RAW_BUCKET)
    blobs = list(bucket.list_blobs(prefix=prefix))
    
    if not blobs:
        context["task_instance"].log.error(f"No files found in {prefix}")
        return "data_quality_failed"
    
    # Check minimum file sizes
    min_size_bytes = 200
    for blob in blobs:
        if blob.size < min_size_bytes:
            context["task_instance"].log.error(
                f"File {blob.name} is too small: {blob.size} bytes"
            )
            return "data_quality_failed"
    
    context["task_instance"].log.info(
        f"Data quality passed: {len(blobs)} files, total size: {sum(b.size for b in blobs)} bytes"
    )
    return "spark_cleanse"


# Task 1: Trigger Cloud Run ingestor
trigger_ingestor = SimpleHttpOperator(
    task_id="trigger_ingestor",
    http_conn_id="ingestor_service",
    endpoint="/ingest/hourly",
    method="POST",
    data={"city": "Bangkok"},
    headers={"Content-Type": "application/json"},
    response_check=lambda response: response.status_code == 200,
    log_response=True,
    dag=dag,
)

# Task 2: Wait for data to land in GCS
wait_for_data = GCSObjectsWithPrefixExistenceSensor(
    task_id="wait_for_data",
    bucket=RAW_BUCKET,
    prefix="{{ get_partition_prefix() }}",
    google_cloud_conn_id="google_cloud_default",
    timeout=600,  # 10 minutes
    poke_interval=30,  # Check every 30 seconds
    mode="poke",
    dag=dag,
)

# Task 3: Data quality gate
data_quality_check = BranchPythonOperator(
    task_id="data_quality_check",
    python_callable=validate_raw_data,
    provide_context=True,
    dag=dag,
)

# Task 4: Submit Spark cleanse job to Dataproc Serverless
spark_cleanse = DataprocSubmitJobOperator(
    task_id="spark_cleanse",
    job={
        "reference": {"project_id": PROJECT_ID},
        "placement": {"cluster_name": ""},  # Serverless doesn't need cluster
        "pyspark_job": {
            "main_python_file_uri": f"gs://{RAW_BUCKET}/spark/cleanse.py",
            "args": [
                "--project_id", PROJECT_ID,
                "--raw_bucket", RAW_BUCKET,
                "--quar_bucket", QUAR_BUCKET,
                "--partition_date", "{{ ds }}",
                "--partition_hour", "{{ execution_date.strftime('%H') }}",
            ],
            "python_file_uris": [
                f"gs://{RAW_BUCKET}/spark/utils.py",
            ],
        },
    },
    region=REGION,
    project_id=PROJECT_ID,
    gcp_conn_id="google_cloud_default",
    dag=dag,
)

# Alternative: Submit as Dataproc Serverless batch
# spark_cleanse_batch = DataprocCreateBatchOperator(
#     task_id="spark_cleanse_batch",
#     project_id=PROJECT_ID,
#     region=REGION,
#     batch={
#         "runtime_config": {
#             "version": "2.1",
#             "properties": {
#                 "spark.executor.instances": "2",
#                 "spark.driver.memory": "2g",
#                 "spark.executor.memory": "2g",
#             }
#         },
#         "environment_config": {
#             "execution_config": {
#                 "service_account": DATAPROC_SA,
#             }
#         },
#         "pyspark_batch": {
#             "main_python_file_uri": f"gs://{RAW_BUCKET}/spark/cleanse.py",
#             "args": [...],
#         },
#     },
#     batch_id=f"aqi-cleanse-{{{{ ds }}}}-{{{{ execution_date.strftime('%H') }}}}",
#     dag=dag,
# )

# Task 5: Run dbt models
dbt_run = BashOperator(
    task_id="dbt_run",
    bash_command="""
    cd /opt/airflow/dbt && \
    dbt run --select staging+ --vars '{"execution_date": "{{ ds }}", "execution_hour": "{{ execution_date.strftime('%H') }}"}' && \
    dbt test --select staging+
    """,
    dag=dag,
)

# Task 6: Handle data quality failure
data_quality_failed = BashOperator(
    task_id="data_quality_failed",
    bash_command='echo "Data quality check failed for {{ ds }} {{ execution_date.strftime(\'%H\') }}:00"',
    trigger_rule=TriggerRule.NONE_FAILED,
    dag=dag,
)

# Task 7: Send failure notification
notify_failure = BashOperator(
    task_id="notify_failure",
    bash_command=f"""
    curl -X POST {SLACK_WEBHOOK_CONN} \
    -H 'Content-Type: application/json' \
    -d '{{"text": "🚨 AQI Pipeline Failed: {{{{ dag.dag_id }}}} on {{{{ ds }}}} {{{{ execution_date.strftime('%H') }}}}:00"}}'
    """,
    trigger_rule=TriggerRule.ONE_FAILED,
    dag=dag,
)

# Task 8: Success notification (optional)
notify_success = BashOperator(
    task_id="notify_success",
    bash_command='echo "✅ AQI Pipeline succeeded for {{ ds }} {{ execution_date.strftime(\'%H\') }}:00"',
    trigger_rule=TriggerRule.ALL_SUCCESS,
    dag=dag,
)

# Define task dependencies
trigger_ingestor >> wait_for_data >> data_quality_check
data_quality_check >> [spark_cleanse, data_quality_failed]
spark_cleanse >> dbt_run >> notify_success
[data_quality_failed, spark_cleanse, dbt_run] >> notify_failure


# Helper function for templating
def get_partition_prefix_template():
    """Template function for partition prefix."""
    return "date={{ ds }}/hour={{ execution_date.strftime('%H') }}/"


# Register template function
dag.user_defined_macros = {
    "get_partition_prefix": get_partition_prefix_template
}
