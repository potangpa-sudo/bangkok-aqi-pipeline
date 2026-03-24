PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
DBT ?= $(if $(wildcard .venv/bin/dbt),.venv/bin/dbt,dbt)
PYTHONPATH=src

.PHONY: install extract dbt-build dashboard test lint airflow-init airflow-up airflow-down deploy-azure-job

install:
	$(PYTHON) -m pip install -e ".[dev]"

extract:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bangkok_aqi.cli extract

dbt-build:
	$(DBT) build --project-dir dbt --profiles-dir dbt

dashboard:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m streamlit run dashboard/app.py

test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check src tests

airflow-init:
	docker compose up airflow-init

airflow-up:
	docker compose up -d airflow-webserver airflow-scheduler

airflow-down:
	docker compose down

deploy-azure-job:
	bash deploy_azure.sh
