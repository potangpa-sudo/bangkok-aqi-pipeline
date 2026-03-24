from __future__ import annotations

import logging
from typing import Any

import requests

from bangkok_aqi.config import get_settings

LOGGER = logging.getLogger(__name__)


def build_airflow_failure_message(context: dict[str, Any]) -> str:
    task_instance = context.get("task_instance")
    dag_run = context.get("dag_run")
    exception = context.get("exception")
    dag = context.get("dag")

    fallback_dag_id = dag.dag_id if dag else "unknown"
    dag_id = getattr(task_instance, "dag_id", fallback_dag_id)
    task_id = getattr(task_instance, "task_id", "unknown")
    run_id = getattr(dag_run, "run_id", context.get("run_id", "unknown"))
    logical_date = context.get("logical_date")

    return (
        "Bangkok AQI pipeline failure detected.\n"
        f"DAG: {dag_id}\n"
        f"Task: {task_id}\n"
        f"Run ID: {run_id}\n"
        f"Logical date: {logical_date}\n"
        f"Error: {exception}"
    )


def send_alert(message: str) -> bool:
    settings = get_settings()
    if not settings.alert_webhook_url:
        LOGGER.info("Skipping alert because ALERT_WEBHOOK_URL is not configured.")
        return False

    response = requests.post(
        settings.alert_webhook_url,
        json={"text": message},
        timeout=10,
    )
    response.raise_for_status()
    return True


def notify_airflow_failure(context: dict[str, Any]) -> None:
    message = build_airflow_failure_message(context)

    try:
        alert_sent = send_alert(message)
    except requests.RequestException:
        LOGGER.exception("Failed to send Airflow alert notification.")
        return

    if alert_sent:
        LOGGER.info("Sent Airflow failure alert for %s", context.get("task_instance"))
