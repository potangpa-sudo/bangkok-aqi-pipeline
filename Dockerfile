FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY dbt/ ./dbt/

RUN pip install --no-cache-dir .

ENV PYTHONPATH=/app/src

CMD ["python", "-m", "bangkok_aqi.cli", "extract"]
