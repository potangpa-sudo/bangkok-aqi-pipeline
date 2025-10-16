# Bangkok AQI Pipeline

[![CI](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/actions/workflows/ci.yml)
[![Deploy](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/actions/workflows/deploy.yml/badge.svg)](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/actions/workflows/deploy.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Terraform](https://img.shields.io/badge/terraform-1.5.0+-purple.svg)](https://www.terraform.io/)

> **Production-Grade Data Engineering Pipeline**: End-to-end cloud data pipeline for real-time air quality monitoring in Bangkok

## 🎯 Overview

This project demonstrates a complete data engineering pipeline that ingests, processes, and visualizes air quality data for Bangkok. Built with modern cloud technologies and best practices, it showcases production-ready data engineering skills.

### Key Features

- **🌐 Real-time Data Ingestion**: Automated hourly data collection from Open-Meteo APIs
- **☁️ Cloud-Native Architecture**: Built on Google Cloud Platform with serverless components
- **🔄 Event-Driven Processing**: Pub/Sub messaging and Airflow orchestration
- **📊 Data Warehousing**: BigQuery with partitioning and clustering for optimal performance
- **🛠️ Infrastructure as Code**: Complete Terraform deployment with reusable modules
- **📈 Interactive Dashboard**: Streamlit-based analytics dashboard
- **✅ Data Quality**: Comprehensive testing with dbt and automated validation
- **🚀 CI/CD Pipeline**: Automated testing, building, and deployment

## 🏗️ Architecture

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

**[See detailed architecture documentation →](docs/architecture.md)**

## 📁 Project Structure

```
bangkok-aqi-pipeline/
├── infra/terraform/              # Infrastructure as Code
│   ├── main.tf                   # Main Terraform configuration
│   ├── modules/                  # Reusable Terraform modules
│   └── README.md
├── src/ingestor/                 # Cloud Run ingestor service
│   ├── app.py                    # FastAPI application
│   ├── clients.py                # GCS & Pub/Sub clients
│   ├── Dockerfile                # Container configuration
│   └── README.md
├── airflow/dags/                 # Airflow DAGs
│   └── aqi_hourly.py             # Hourly pipeline orchestration
├── spark/                        # PySpark cleansing jobs
│   ├── cleanse.py                # Main Spark job
│   ├── job_config.json           # Dataproc configuration
│   └── README.md
├── dbt/                          # dbt transformation project
│   ├── models/                   # SQL models
│   ├── dbt_project.yml
│   └── README.md
├── app/                          # Streamlit dashboard
│   ├── dashboard_bq.py           # BigQuery-backed dashboard
│   ├── Dockerfile
│   └── requirements.txt
├── .github/workflows/            # CI/CD pipelines
│   ├── ci.yml                    # Continuous integration
│   └── deploy.yml                # Deployment pipeline
├── docs/                         # Documentation
│   └── architecture.md           # Architecture & runbook
└── README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites

- GCP Project with billing enabled
- `gcloud` CLI authenticated
- Terraform >= 1.5.0
- Python 3.11+
- Docker (for local testing)

### 1. Clone and Configure

```bash
git clone https://github.com/potangpa-sudo/bangkok-aqi-pipeline.git
cd bangkok-aqi-pipeline

# Copy and configure environment
cp .env.example .env
# Edit .env with your GCP project details
```

### 2. Deploy Infrastructure

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your configuration

terraform init
terraform plan
terraform apply
```

### 3. Deploy Services

```bash
# Build and deploy services
cd ../../src/ingestor
gcloud builds submit --tag gcr.io/${PROJECT_ID}/aqi-ingestor
gcloud run deploy aqi-ingestor --image gcr.io/${PROJECT_ID}/aqi-ingestor

cd ../../app
gcloud builds submit --tag gcr.io/${PROJECT_ID}/aqi-dashboard
gcloud run deploy aqi-dashboard --image gcr.io/${PROJECT_ID}/aqi-dashboard
```

### 4. Run Pipeline

```bash
# Trigger manual ingestion
INGESTOR_URL=$(terraform output -raw ingestor_service_url)
curl -X POST "${INGESTOR_URL}/ingest/hourly?city=Bangkok"

# View dashboard
DASHBOARD_URL=$(terraform output -raw dashboard_service_url)
open ${DASHBOARD_URL}
```

**[See complete deployment guide →](DEPLOYMENT.md)**

## 💻 Local Development

The project includes a local development mode for testing and development:

```bash
# Setup local environment
make setup

# Run local pipeline
make run

# Run tests
make test

# Launch local dashboard
make dashboard
```

## 📊 Data Model

The pipeline follows a layered data architecture:

1. **Raw Layer**: Unprocessed API responses stored in GCS
2. **Staging Layer**: Cleaned and validated data in BigQuery
3. **Fact Layer**: Combined hourly observations
4. **Mart Layer**: Daily aggregates for analytics

## 🧪 Testing

### Automated Testing

- **Python**: Unit tests with pytest
- **SQL**: dbt model testing
- **Terraform**: Configuration validation
- **Docker**: Container builds

### Data Quality

- Schema validation
- Completeness checks
- Freshness monitoring
- Automated alerts

## 📈 Monitoring & Observability

- **Cloud Monitoring**: Infrastructure metrics and uptime
- **Cloud Logging**: Centralized logs from all services
- **Airflow UI**: DAG runs and task execution
- **BigQuery**: Query performance and data freshness

## 💰 Cost Management

**Estimated monthly cost: ~$105 USD**

- Cloud Composer (Small): $75
- Dataproc Serverless: $15
- BigQuery: $10
- GCS: $3
- Cloud Run: $1
- Other: $1

## 🔒 Security

- All secrets managed in Secret Manager
- Least-privilege IAM roles per service
- Data encrypted at rest and in transit
- Audit logging enabled

## 📚 Documentation

- **[Architecture & Runbook](docs/architecture.md)** - System design and operations
- **[Deployment Guide](DEPLOYMENT.md)** - Step-by-step deployment instructions
- **[Terraform README](infra/terraform/README.md)** - Infrastructure deployment
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Commit using conventional commits (`git commit -m 'feat: add amazing feature'`)
5. Push to your branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Open-Meteo](https://open-meteo.com/) for providing free weather and AQI APIs
- [Google Cloud Platform](https://cloud.google.com/) for cloud infrastructure
- [dbt Labs](https://www.getdbt.com/) for the transformation framework
- [Apache Airflow](https://airflow.apache.org/) for workflow orchestration
- [Terraform](https://www.terraform.io/) for infrastructure-as-code

## 📞 Support

- **Issues**: [Report a bug](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/issues/new?template=bug_report.md)
- **Feature Requests**: [Request a feature](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/issues/new?template=feature_request.md)
- **Discussions**: [GitHub Discussions](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/discussions)

---

**Built with ❤️ for the data engineering community**