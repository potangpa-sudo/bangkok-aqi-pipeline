# Bangkok AQI Pipeline

# Bangkok AQI Pipeline

[![CI](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/actions/workflows/ci.yml)
[![Deploy](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/actions/workflows/deploy.yml/badge.svg)](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/actions/workflows/deploy.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Terraform](https://img.shields.io/badge/terraform-1.5.0+-purple.svg)](https://www.terraform.io/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> **Production-Grade Data Engineering Project**: End-to-end cloud data pipeline for real-time air quality monitoring in Bangkok

[Features](#-key-features) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

[![CI](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/workflows/CI/badge.svg)](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/actions)
[![Deploy](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/workflows/Deploy%20to%20GCP/badge.svg)](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/actions)

## 🎯 Project Evolution

### Before (Local Prototype)
- ✅ Local ingestion with Python scripts
- ✅ DuckDB for data warehouse
- ✅ SQL transformations
- ✅ Streamlit dashboard
- ❌ No orchestration
- ❌ No scalability
- ❌ No monitoring
- ❌ Manual deployment

### After (GCP Production Pipeline)
- ✅ **Cloud Run** serverless ingestor (FastAPI)
- ✅ **GCS** for raw data with partitioning
- ✅ **Pub/Sub** event-driven architecture
- ✅ **Dataproc Serverless** for Spark cleansing
- ✅ **BigQuery** data warehouse with partitioning/clustering
- ✅ **dbt** for transformations with testing
- ✅ **Cloud Composer (Airflow)** for orchestration
- ✅ **Terraform** infrastructure-as-code
- ✅ **GitHub Actions** CI/CD pipeline
- ✅ **Cloud Run** Streamlit dashboard
- ✅ Comprehensive monitoring, alerting, and cost optimization

## 📊 What This Demonstrates

### For Data Engineers
- Building production pipelines with GCP services
- Infrastructure-as-code with Terraform
- Event-driven architecture (Pub/Sub)
- Partitioning and clustering strategies
- Incremental data processing
- Data quality testing (dbt)
- CI/CD for data pipelines

### For Platform Engineers
- Multi-service GCP deployment
- IAM least-privilege configuration
- Secret management
- Cost optimization strategies
- Monitoring and observability
- Disaster recovery planning

### For Hiring Managers
- End-to-end ownership (ingestion → serving)
- Modern tooling (dbt, Terraform, Airflow)
- Best practices (IaC, testing, documentation)
- Scalable architecture
- Cost consciousness
- Production-ready code

## 🏗️ Architecture Overview

```
Open-Meteo API → Cloud Run (Ingestor) → GCS (Raw) → Pub/Sub
                                                        ↓
                                          Cloud Composer (Airflow)
                                                        ↓
                                  Dataproc Spark (Cleanse) → BigQuery (Staging)
                                                                      ↓
                                                        dbt (Transform) → BigQuery (Marts)
                                                                                  ↓
                                                                Cloud Run (Dashboard)
```

**[See detailed architecture diagram and docs →](docs/architecture.md)**

## 📁 Project Structure

```
bangkok-aqi-pipeline/
├── infra/terraform/              # Infrastructure-as-code
│   ├── main.tf                   # Main Terraform config
│   ├── modules/                  # Reusable modules
│   │   ├── iam/                  # Service accounts & permissions
│   │   ├── storage/              # GCS buckets
│   │   ├── pubsub/               # Pub/Sub topics
│   │   ├── bq/                   # BigQuery datasets
│   │   ├── run/                  # Cloud Run services
│   │   ├── composer/             # Cloud Composer
│   │   ├── dataproc_serverless/  # Dataproc config
│   │   └── secrets/              # Secret Manager
│   └── README.md
├── src/ingestor/                 # Cloud Run ingestor service
│   ├── app.py                    # FastAPI application
│   ├── clients.py                # GCS & Pub/Sub clients
│   ├── utils.py                  # Helper functions
│   ├── Dockerfile                # Container image
│   └── README.md
├── airflow/dags/                 # Airflow DAGs
│   └── aqi_hourly.py             # Hourly pipeline orchestration
├── spark/                        # PySpark cleansing jobs
│   ├── cleanse.py                # Main Spark job
│   ├── job_config.json           # Dataproc config
│   └── README.md
├── dbt/                          # dbt transformation project
│   ├── models/
│   │   ├── staging/              # Staging views
│   │   └── marts/                # Production tables
│   ├── dbt_project.yml
│   └── README.md
├── app/                          # Streamlit dashboard
│   ├── dashboard_bq.py           # BigQuery-backed dashboard
│   ├── Dockerfile                # Container image
│   └── requirements.txt
├── .github/workflows/            # CI/CD pipelines
│   ├── ci.yml                    # Continuous integration
│   └── deploy.yml                # Deployment pipeline
├── docs/                         # Documentation
│   └── architecture.md           # Architecture & runbook
├── sql/                          # Legacy local SQL (preserved)
├── src/                          # Legacy local pipeline (preserved)
├── data/                         # Local data (development only)
└── README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites

- GCP Project with billing enabled
- `gcloud` CLI authenticated
- Terraform >= 1.5.0
- Python 3.11+
- Docker (for local testing)

### 1. Clone Repository

```bash
git clone https://github.com/potangpa-sudo/bangkok-aqi-pipeline.git
cd bangkok-aqi-pipeline
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your GCP project details
nano .env
```

### 3. Deploy Infrastructure

```bash
cd infra/terraform

# Initialize Terraform
terraform init

# Review planned changes
terraform plan -var-file=terraform.tfvars

# Deploy
terraform apply

# Save outputs
terraform output -json > outputs.json
```

### 4. Deploy Services

```bash
# Build and deploy Cloud Run ingestor
cd ../../src/ingestor
gcloud builds submit --tag gcr.io/${PROJECT_ID}/aqi-ingestor
gcloud run deploy aqi-ingestor --image gcr.io/${PROJECT_ID}/aqi-ingestor --region asia-southeast1

# Build and deploy Cloud Run dashboard
cd ../../app
gcloud builds submit --tag gcr.io/${PROJECT_ID}/aqi-dashboard
gcloud run deploy aqi-dashboard --image gcr.io/${PROJECT_ID}/aqi-dashboard --region asia-southeast1

# Upload Spark job to GCS
cd ../spark
gsutil cp cleanse.py gs://${GCS_BUCKET_RAW}/spark/

# Upload Airflow DAG to Composer
cd ../airflow/dags
gcloud composer environments storage dags import \
  --environment bangkok-aqi-composer \
  --location asia-southeast1 \
  --source aqi_hourly.py
```

### 5. Run Initial Pipeline

```bash
# Trigger manual ingestion
INGESTOR_URL=$(terraform output -raw ingestor_service_url)
curl -X POST "${INGESTOR_URL}/ingest/hourly?city=Bangkok"

# Check Airflow DAG
AIRFLOW_URL=$(terraform output -raw composer_airflow_uri)
open ${AIRFLOW_URL}

# View dashboard
DASHBOARD_URL=$(terraform output -raw dashboard_service_url)
open ${DASHBOARD_URL}
```

## 💻 Local Development (Legacy Mode)

The original local DuckDB pipeline is preserved for development and testing:

```bash
# Setup
make setup

# Run local pipeline
make run

# Run tests
make test

# Launch local dashboard
make dashboard
```

### Core Make Targets

- `make setup` – install dependencies and prepare folders.
- `make run` – full ingestion + transformation run (`python -m src.pipeline`).
- `make transform` – re-run only the SQL models against existing raw tables.
- `make test` – lightweight data quality assertions.
- `make dashboard` – start Streamlit in headless mode.
- `make all` – setup, run, and test in sequence.

### Configuration

Environment variables (loaded from `.env` when present):

- `LAT` / `LON` – coordinates for Bangkok (defaults provided).
- `BOOTSTRAP_HOURS` – number of trailing hours to retain when ingesting (default `72`).
- `TIMEZONE` – timezone passed to Open-Meteo (default `Asia/Bangkok`).

## Data Model

ASCII ERD of the DuckDB structures:

```
+-------------------+        +-----------------------+
| raw.raw_weather   |        | raw.raw_air_quality   |
+-------------------+        +-----------------------+
            \                        /
             v                      v
      stg.stg_weather       stg.stg_air_quality
             \                      /
              v                    v
             stg.dim_datetime (hour grain)
                       |
                       v
              fct.aqi_by_hour (hour grain)
                       |
                       v
           mart.daily_aqi_weather (day grain)
```

`mart.daily_aqi_weather` exposes daily averages for PM2.5, temperature, humidity, precipitation, wind, plus a simple PM2.5-based AQI proxy (rounded `pm2_5 * 4`).

## Testing

`make test` validates:

- Required tables exist (`raw.raw_weather`, `raw.raw_air_quality`, `mart.daily_aqi_weather`).
- Each table contains rows.
- The mart has data within the last three days.

## Streamlit Dashboard

The dashboard displays:

- KPI cards for latest daily PM2.5, temperature, and humidity.
- A line chart tracking PM2.5 and temperature over time.
- A bar chart showing the PM2.5 proxy AQI.
- The trailing daily observations table.

Data is read-only; the app never calls external APIs.

## 📚 Documentation

- **[Architecture & Runbook](docs/architecture.md)** - System design, data flow, SLOs, incident response
- **[Terraform README](infra/terraform/README.md)** - Infrastructure deployment guide
- **[Ingestor README](src/ingestor/README.md)** - Cloud Run service documentation
- **[Spark README](spark/README.md)** - PySpark job documentation
- **[dbt README](dbt/README.md)** - dbt project documentation

## 🧪 Testing

### CI Pipeline (Automated)

Every PR triggers:
- Python linting (ruff)
- Type checking (mypy)
- SQL linting (sqlfluff)
- Terraform validation
- dbt compilation
- Docker builds

### Manual Testing

```bash
# Test ingestor locally
cd src/ingestor
docker build -t aqi-ingestor .
docker run -p 8080:8080 aqi-ingestor
curl http://localhost:8080/healthz

# Test Spark job locally
cd spark
spark-submit cleanse.py --help

# Test dbt models
cd dbt
dbt compile
dbt test
```

## 📊 Monitoring & Observability

- **Cloud Monitoring**: Infrastructure metrics, uptime, costs
- **Cloud Logging**: Centralized logs from all services
- **Airflow UI**: DAG runs, task logs, execution history
- **BigQuery**: Query performance, data freshness
- **Custom Dashboards**: Business KPIs in Looker Studio (optional)

## 💰 Cost Management

**Estimated monthly cost: ~$105 USD**

- Cloud Composer (Small): $75
- Dataproc Serverless: $15
- BigQuery: $10
- GCS: $3
- Cloud Run: $1
- Other: $1

**Zero-cost mode** (for learning):
- Use BigQuery Sandbox (free tier)
- Use Dataproc Serverless free tier
- Deploy only ingestor + dashboard (skip Composer)

## 🔒 Security

- All secrets in Secret Manager (no plaintext)
- Least-privilege IAM roles per service
- VPC-SC ready (optional)
- Audit logging enabled
- Data encrypted at rest and in transit

## 🔧 Troubleshooting

### Common Issues

**Terraform apply fails**:
```bash
# Check GCP APIs are enabled
gcloud services enable compute.googleapis.com storage.googleapis.com bigquery.googleapis.com

# Verify permissions
gcloud auth list
```

**Cloud Run deployment fails**:
```bash
# Check service account exists
gcloud iam service-accounts list

# Check image exists
gcloud container images list
```

**Airflow DAG not appearing**:
```bash
# Check DAG syntax
python airflow/dags/aqi_hourly.py

# Check Composer bucket
gcloud composer environments storage dags list --environment bangkok-aqi-composer
```

**dbt models fail**:
```bash
# Verify BigQuery connection
dbt debug

# Check source data exists
dbt source freshness
```

## 🛠️ Development Workflow

1. **Feature branch**: Create from `main`
2. **Local development**: Test changes locally
3. **PR**: Open pull request with description
4. **CI**: Automated checks run
5. **Review**: Code review by team
6. **Merge**: Merge to `main`
7. **Deploy**: Automated deployment to GCP

## 📈 Future Enhancements

- [ ] Implement official Thailand AQI formula
- [ ] Add more cities (multi-region support)
- [ ] Real-time streaming (Pub/Sub → Dataflow → BigQuery)
- [ ] ML models for AQI prediction
- [ ] Mobile app (Flutter + Firebase)
- [ ] Looker Studio embedded reports
- [ ] Data quality monitoring (Great Expectations)
- [ ] Cost anomaly detection

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Start for Contributors
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Commit using conventional commits (`git commit -m 'feat: add amazing feature'`)
5. Push to your branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## � Security

Found a security vulnerability? Please read our [Security Policy](SECURITY.md) for responsible disclosure guidelines.

## �📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Open-Meteo](https://open-meteo.com/) for providing free weather and AQI APIs
- [Google Cloud Platform](https://cloud.google.com/) for cloud infrastructure
- [dbt Labs](https://www.getdbt.com/) for the transformation framework
- [Apache Airflow](https://airflow.apache.org/) for workflow orchestration
- [Terraform](https://www.terraform.io/) for infrastructure-as-code
- All contributors and supporters of this project

## 👤 Author

**@potangpa-sudo**
- GitHub: [@potangpa-sudo](https://github.com/potangpa-sudo)
- Project: [Bangkok AQI Pipeline](https://github.com/potangpa-sudo/bangkok-aqi-pipeline)

## 📞 Contact & Support

- **Issues**: [Report a bug](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/issues/new?template=bug_report.md)
- **Feature Requests**: [Request a feature](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/issues/new?template=feature_request.md)
- **Discussions**: [GitHub Discussions](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/discussions)

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/potangpa-sudo/bangkok-aqi-pipeline?style=social)
![GitHub forks](https://img.shields.io/github/forks/potangpa-sudo/bangkok-aqi-pipeline?style=social)
![GitHub issues](https://img.shields.io/github/issues/potangpa-sudo/bangkok-aqi-pipeline)
![GitHub last commit](https://img.shields.io/github/last-commit/potangpa-sudo/bangkok-aqi-pipeline)

---

## 📊 Before vs After Comparison Table

| Feature | Local (Before) | GCP Production (After) |
|---------|---------------|------------------------|
| **Ingestion** | Python script (manual) | Cloud Run + FastAPI (automated) |
| **Storage** | Local file system | GCS with partitioning & lifecycle |
| **Processing** | pandas (in-memory) | Dataproc Spark (distributed) |
| **Warehouse** | DuckDB (file-based) | BigQuery (cloud-native) |
| **Transforms** | SQL scripts | dbt with testing |
| **Orchestration** | Manual execution | Cloud Composer (Airflow) |
| **Dashboard** | Local Streamlit | Cloud Run + Streamlit |
| **Monitoring** | None | Cloud Monitoring + Logging |
| **CI/CD** | None | GitHub Actions |
| **Infrastructure** | Manual setup | Terraform (IaC) |
| **Scalability** | Single machine | Auto-scaling, serverless |
| **Cost** | $0 (local) | ~$105/month (production) |
| **Data Quality** | Basic checks | dbt tests + Great Expectations |
| **Security** | Local only | IAM, Secret Manager, encryption |
| **Disaster Recovery** | Manual backup | Automatic backups, time travel |

## What This Demonstrates to Recruiters

- Ability to design and implement an end-to-end data pipeline with clear layering.
- Comfort combining Python ingestion, SQL transformations, and lightweight orchestration.
- Pragmatic data quality testing embedded alongside the pipeline.
- Skill presenting insights through a polished Streamlit dashboard tied to the warehouse.
- Familiarity with modern tooling (DuckDB, pandas, Makefile automation, environment-driven config).

Happy hacking!
