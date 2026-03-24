from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import Mock

import requests

from bangkok_aqi import alerts


@dataclass
class FakeTaskInstance:
    dag_id: str
    task_id: str


@dataclass
class FakeDagRun:
    run_id: str


def test_build_airflow_failure_message_includes_context() -> None:
    message = alerts.build_airflow_failure_message(
        {
            "task_instance": FakeTaskInstance(
                dag_id="bangkok_aqi_pipeline",
                task_id="build_dbt_models",
            ),
            "dag_run": FakeDagRun(run_id="manual__2026-03-24T08:00:00+00:00"),
            "logical_date": "2026-03-24T08:00:00+00:00",
            "exception": RuntimeError("dbt test failed"),
        }
    )

    assert "DAG: bangkok_aqi_pipeline" in message
    assert "Task: build_dbt_models" in message
    assert "Run ID: manual__2026-03-24T08:00:00+00:00" in message
    assert "Error: dbt test failed" in message


def test_send_alert_skips_when_webhook_not_configured(monkeypatch) -> None:
    monkeypatch.setattr(
        alerts,
        "get_settings",
        lambda: Mock(alert_webhook_url=None),
    )

    assert alerts.send_alert("test alert") is False


def test_send_alert_posts_to_configured_webhook(monkeypatch) -> None:
    post_mock = Mock()
    response_mock = Mock()
    post_mock.return_value = response_mock

    monkeypatch.setattr(
        alerts,
        "get_settings",
        lambda: Mock(alert_webhook_url="https://example.com/webhook"),
    )
    monkeypatch.setattr(alerts.requests, "post", post_mock)

    assert alerts.send_alert("test alert") is True
    post_mock.assert_called_once_with(
        "https://example.com/webhook",
        json={"text": "test alert"},
        timeout=10,
    )
    response_mock.raise_for_status.assert_called_once_with()


def test_notify_airflow_failure_handles_request_errors(monkeypatch) -> None:
    send_alert_mock = Mock(side_effect=requests.RequestException("network failure"))
    monkeypatch.setattr(alerts, "send_alert", send_alert_mock)

    alerts.notify_airflow_failure(
        {
            "task_instance": FakeTaskInstance(
                dag_id="bangkok_aqi_pipeline",
                task_id="extract_raw_aqi",
            ),
            "dag_run": FakeDagRun(run_id="scheduled__2026-03-24T09:00:00+00:00"),
            "logical_date": "2026-03-24T09:00:00+00:00",
            "exception": RuntimeError("upstream API failed"),
        }
    )

    send_alert_mock.assert_called_once()
