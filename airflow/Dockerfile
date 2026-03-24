FROM apache/airflow:2.10.3-python3.11

USER root

COPY pyproject.toml README.md /opt/airflow/project/
COPY src /opt/airflow/project/src
COPY dbt /opt/airflow/project/dbt

RUN chown -R airflow:0 /opt/airflow/project

USER airflow

RUN pip install --no-cache-dir psycopg2-binary && \
    pip install --no-cache-dir /opt/airflow/project[dev]
