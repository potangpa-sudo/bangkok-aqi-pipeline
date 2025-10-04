# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Add retry logic with exponential backoff to API calls
- Implement data lineage tracking
- Add more comprehensive integration tests
- Support for multiple cities beyond Bangkok
- Real-time alerting for air quality thresholds

## [1.0.0] - 2025-10-05

### Added
- **Infrastructure as Code (Terraform)**
  - Complete GCP infrastructure with 8 reusable modules
  - IAM configuration with least-privilege service accounts
  - Storage (GCS) with lifecycle policies
  - Pub/Sub topics and subscriptions
  - BigQuery datasets with partitioning and clustering
  - Cloud Run service definitions
  - Cloud Composer (Airflow) environment
  - Dataproc Serverless configuration
  - Secret Manager integration

- **Data Ingestion Service**
  - FastAPI application for hourly data ingestion
  - GCS client for partitioned data storage
  - Pub/Sub client for event publishing
  - Pydantic schemas for data validation
  - Docker containerization
  - Health check endpoints
  - Comprehensive error handling

- **Data Processing (Spark)**
  - PySpark job for data cleansing and normalization
  - Quarantine logic for invalid data
  - BigQuery upserts with MERGE semantics
  - Dataproc Serverless compatibility
  - Configurable batch processing

- **Orchestration (Airflow)**
  - Hourly DAG with 8 tasks
  - GCS existence sensors
  - HTTP operators for API triggers
  - Dataproc job submission
  - dbt model execution
  - Failure notifications
  - Quality gate checks

- **Data Transformations (dbt)**
  - 5 SQL models (staging, facts, marts)
  - Staging models for weather and AQI data
  - Dimension tables (datetime)
  - Fact tables (hourly AQI)
  - Mart tables (daily aggregates)
  - 20+ data quality tests
  - Model documentation

- **Analytics Dashboard**
  - Streamlit application with dual-mode support
  - DuckDB for local development
  - BigQuery for production
  - KPI cards with trends
  - Time series visualizations
  - Correlation analysis
  - Data quality metrics
  - Docker containerization

- **CI/CD Pipelines**
  - GitHub Actions workflow for continuous integration
  - Automated linting (Ruff)
  - Type checking (mypy)
  - Terraform validation
  - dbt compilation
  - SQL linting
  - Docker image builds
  - Continuous deployment workflow
  - Automated infrastructure deployment
  - Service deployments to Cloud Run
  - Spark job uploads
  - dbt model execution
  - Smoke tests

- **Documentation**
  - Comprehensive README with project overview
  - Step-by-step DEPLOYMENT guide
  - Architecture documentation (5000+ words)
  - Component-specific READMEs
  - API documentation
  - Cost estimates and optimization tips
  - IAM permissions matrix
  - Runbook for operations
  - CONTRIBUTING guidelines
  - Code of Conduct
  - Security policy
  - Pull request template
  - Issue templates (bug report, feature request)

- **Development Tools**
  - pyproject.toml with Ruff, mypy, pytest configuration
  - Pre-commit hooks
  - Development environment setup scripts
  - Example environment files
  - MIT License

### Infrastructure
- GCS buckets with lifecycle policies (90-day retention)
- BigQuery datasets partitioned by date, clustered by hour
- Cloud Run services with autoscaling (0-10 instances)
- Cloud Composer environment (small size, 1 node)
- Dataproc Serverless batch execution
- Pub/Sub with dead letter topics
- Secret Manager for sensitive data

### Performance
- Partitioned data storage by date/hour
- BigQuery clustering for query optimization
- Cloud Run autoscaling (0-10 instances)
- dbt incremental models
- Efficient Spark joins and aggregations

### Cost Optimization
- Cloud Run scales to zero
- Dataproc Serverless (pay per use)
- Storage lifecycle policies
- Small Composer environment
- Estimated monthly cost: ~$105

### Security
- Least privilege IAM roles
- Service account per component
- Secret Manager integration
- No hardcoded credentials
- Input validation with Pydantic
- HTTPS for all communications

## [0.1.0] - 2024-10-04 (Local Version)

### Initial Features
- Local DuckDB-based pipeline
- Manual data ingestion scripts
- Basic Streamlit dashboard
- Simple data transformations
- Local file storage

---

## Release Notes

### Version 1.0.0 - Production Release

This is the first production-ready release of the Bangkok AQI Pipeline. The system has been completely rewritten to run on Google Cloud Platform with enterprise-grade features:

**Highlights:**
- ✅ Fully automated hourly data ingestion
- ✅ Scalable infrastructure with auto-scaling
- ✅ Comprehensive data quality checks
- ✅ Production-ready monitoring and alerting
- ✅ CI/CD pipeline for automated deployments
- ✅ Complete documentation and runbooks

**Breaking Changes from 0.1.0:**
- Migrated from local DuckDB to GCP BigQuery
- Changed from manual scripts to automated Airflow orchestration
- Updated dashboard to support both local and cloud modes
- New infrastructure requirements (GCP account, Terraform)

**Migration Guide:**
See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions.

**Known Issues:**
- Cloud Composer environment creation takes 20-30 minutes
- Initial Terraform apply requires multiple API enables
- Dashboard requires BigQuery access for production mode

**Contributors:**
- @potangpa-sudo - Initial development and architecture

---

## Versioning Strategy

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: Backwards-compatible functionality additions
- **PATCH**: Backwards-compatible bug fixes

## How to Report Issues

Found a bug or have a feature request? Please:
1. Check existing [Issues](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/issues)
2. Create a new issue using the appropriate template
3. Provide as much detail as possible

---

**Legend:**
- `Added` - New features
- `Changed` - Changes in existing functionality
- `Deprecated` - Soon-to-be removed features
- `Removed` - Removed features
- `Fixed` - Bug fixes
- `Security` - Security improvements
