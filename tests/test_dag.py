from __future__ import annotations

import importlib.util
import sys
import types
from datetime import datetime, timedelta
from pathlib import Path


class FakeAirflowFailException(Exception):
    pass


def load_dag_module():
    dag_path = Path(__file__).resolve().parents[1] / "dags" / "bangkok_aqi_pipeline.py"
    active_dag = None

    class FakeDAG:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.tasks = []

        def __enter__(self):
            nonlocal active_dag
            active_dag = self
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            nonlocal active_dag
            active_dag = None
            return False

    class FakeOperator:
        def __init__(self, task_id: str, **kwargs):
            self.task_id = task_id
            self.kwargs = kwargs
            self.downstream_task_ids: set[str] = set()
            active_dag.tasks.append(self)

        def __rshift__(self, other):
            self.downstream_task_ids.add(other.task_id)
            return other

    airflow_module = types.ModuleType("airflow")
    airflow_module.DAG = FakeDAG

    airflow_exceptions = types.ModuleType("airflow.exceptions")
    airflow_exceptions.AirflowFailException = FakeAirflowFailException

    airflow_operators = types.ModuleType("airflow.operators")
    airflow_operators_bash = types.ModuleType("airflow.operators.bash")
    airflow_operators_bash.BashOperator = FakeOperator
    airflow_operators_python = types.ModuleType("airflow.operators.python")
    airflow_operators_python.PythonOperator = FakeOperator

    pendulum_module = types.ModuleType("pendulum")
    pendulum_module.datetime = lambda year, month, day, tz=None: datetime(year, month, day)
    pendulum_module.duration = lambda minutes=0: timedelta(minutes=minutes)

    module_overrides = {
        "airflow": airflow_module,
        "airflow.exceptions": airflow_exceptions,
        "airflow.operators": airflow_operators,
        "airflow.operators.bash": airflow_operators_bash,
        "airflow.operators.python": airflow_operators_python,
        "pendulum": pendulum_module,
    }
    original_modules = {name: sys.modules.get(name) for name in module_overrides}
    sys.modules.update(module_overrides)

    try:
        spec = importlib.util.spec_from_file_location("test_bangkok_aqi_pipeline_dag", dag_path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        for name, original_module in original_modules.items():
            if original_module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = original_module


def test_bangkok_aqi_pipeline_dag_defines_bronze_silver_gold_flow() -> None:
    module = load_dag_module()
    dag = module.dag
    tasks = {task.task_id: task for task in dag.tasks}

    assert dag.kwargs["dag_id"] == "bangkok_aqi_pipeline"
    assert dag.kwargs["schedule"] == "0 * * * *"
    assert set(tasks) == {
        "extract_raw_aqi_json",
        "extract_raw_weather_json",
        "build_silver_models",
        "build_gold_mart",
    }
    assert tasks["extract_raw_aqi_json"].downstream_task_ids == {"build_silver_models"}
    assert tasks["extract_raw_weather_json"].downstream_task_ids == {"build_silver_models"}
    assert tasks["build_silver_models"].downstream_task_ids == {"build_gold_mart"}


def test_bangkok_aqi_pipeline_dag_configures_task_retries_and_dbt_selects() -> None:
    module = load_dag_module()
    tasks = {task.task_id: task for task in module.dag.tasks}

    assert (
        tasks["extract_raw_aqi_json"].kwargs["python_callable"]
        is module.extract_raw_aqi_json_task
    )
    assert (
        tasks["extract_raw_weather_json"].kwargs["python_callable"]
        is module.extract_raw_weather_json_task
    )
    assert tasks["extract_raw_aqi_json"].kwargs["retries"] == 2
    assert tasks["extract_raw_weather_json"].kwargs["retries"] == 2
    assert "base_aqi_hourly_exploded" in tasks["build_silver_models"].kwargs["bash_command"]
    assert "base_weather_hourly_exploded" in tasks["build_silver_models"].kwargs["bash_command"]
    assert "stg_aqi_hourly" in tasks["build_silver_models"].kwargs["bash_command"]
    assert "stg_weather_hourly" in tasks["build_silver_models"].kwargs["bash_command"]
    assert tasks["build_gold_mart"].kwargs["bash_command"].endswith(
        "--select fct_aqi_hourly"
    )
