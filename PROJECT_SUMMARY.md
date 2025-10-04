# Bangkok AQI Pipeline - GCP Capstone Project

## Executive Summary

This project transforms a local Bangkok air quality pipeline into a production-grade, cloud-native data platform on Google Cloud Platform. It demonstrates end-to-end data engineering skills, from infrastructure provisioning to data visualization.

## Key Achievements

### ✅ Infrastructure as Code (Terraform)
- **14 Terraform modules** covering all GCP services
- Modular, reusable design
- Complete IAM configuration with least-privilege
- Automated deployment with `terraform apply`

### ✅ Cloud-Native Ingestion (Cloud Run + FastAPI)
- **Serverless REST API** for data ingestion
- Partitioned writes to GCS (Hive format: `date=YYYY-MM-DD/hour=HH/`)
- Event-driven with Pub/Sub notifications
- Health checks and structured logging

### ✅ Distributed Processing (Dataproc Serverless + Spark)
- **PySpark job** for cleansing and normalization
- Handles bad records (quarantine to separate bucket)
- Upsert to BigQuery with MERGE semantics
- Idempotent and replayable

### ✅ Modern Data Transformation (dbt + BigQuery)
- **5 dbt models**: staging → dimensions → facts → marts
- Incremental processing for efficiency
- Comprehensive data quality tests
- Automatic partitioning and clustering

### ✅ Production Orchestration (Cloud Composer / Airflow)
- **Hourly DAG** with 8 tasks
- Sensor for data availability
- Data quality gates
- Failure notifications (Slack)

### ✅ CI/CD Pipeline (GitHub Actions)
- **Automated testing**: lint, type-check, compile
- **Automated deployment**: build, push, deploy
- **Manual approval** for production changes
- **Smoke tests** after deployment

### ✅ Interactive Dashboard (Cloud Run + Streamlit)
- Dual-mode: local DuckDB (dev) + BigQuery (prod)
- KPI cards, trend charts, data tables
- Auto-refresh with caching

### ✅ Comprehensive Documentation
- Architecture diagrams
- Runbook with incident response procedures
- Cost breakdown and optimization tips
- SLOs and monitoring strategy

## Technical Highlights

### Data Architecture
- **Raw Layer**: GCS with partitioning (date + hour)
- **Staging Layer**: BigQuery hourly partitions
- **Marts Layer**: BigQuery daily aggregates
- **Serving Layer**: BigQuery materialized views

### Code Quality
- **Python**: Type hints, docstrings, structured logging
- **SQL**: dbt best practices, tests, documentation
- **Terraform**: Modules, outputs, variables
- **CI/CD**: Linting, testing, deployment

### Scalability
- **Serverless**: Auto-scaling Cloud Run and Dataproc
- **Partitioning**: Efficient BigQuery queries
- **Incremental**: Only process new data
- **Caching**: Dashboard query optimization

### Cost Optimization
- **$105/month** for production workload
- Zero-cost mode available (BQ Sandbox + free tiers)
- Lifecycle policies for storage
- Min instances = 0 for Cloud Run

## Comparison: Before vs After

| Aspect | Local Pipeline | GCP Pipeline |
|--------|----------------|--------------|
| **Lines of Code** | ~800 | ~3,500 |
| **Files Created** | 15 | 60+ |
| **GCP Services** | 0 | 10+ |
| **Deployment Time** | 5 min (manual) | 20 min (automated) |
| **Monthly Cost** | $0 | ~$105 |
| **Scalability** | 1 machine | Unlimited |
| **Monitoring** | None | Full observability |
| **Data Quality** | Basic | Comprehensive |

## Skills Demonstrated

### For Data Engineers
- [x] Cloud data warehousing (BigQuery)
- [x] Distributed processing (Spark)
- [x] Data modeling (dbt)
- [x] Pipeline orchestration (Airflow)
- [x] Partitioning and clustering
- [x] Incremental processing
- [x] Data quality testing

### For Platform Engineers
- [x] Infrastructure as Code (Terraform)
- [x] Multi-service GCP deployment
- [x] IAM and security
- [x] CI/CD pipelines
- [x] Containerization (Docker)
- [x] Serverless architecture
- [x] Cost optimization

### For Everyone
- [x] Problem decomposition
- [x] Documentation
- [x] Code organization
- [x] Best practices
- [x] Production mindset

## Deployment Instructions

See **[Quick Start](#-quick-start)** in main README.md

## Lessons Learned

1. **Terraform is powerful but complex** - Modular design is essential
2. **dbt transforms SQL development** - Tests are game-changing
3. **Serverless reduces ops burden** - But adds some complexity
4. **Monitoring is non-negotiable** - Plan for observability from day 1
5. **Cost awareness matters** - Small optimizations add up

## Next Steps

If continuing this project:
1. Add ML for AQI prediction
2. Expand to more cities (multi-region)
3. Implement streaming (Pub/Sub → Dataflow)
4. Add Great Expectations for DQ
5. Migrate to dbt Cloud for easier scheduling

## Recruiter-Friendly Summary

**"Built a production-grade, event-driven data pipeline on GCP using Cloud Run, Dataproc Spark, BigQuery, dbt, and Airflow, with full IaC (Terraform) and CI/CD (GitHub Actions). Ingests hourly weather and air quality data, processes with distributed Spark, transforms with dbt, and serves via Streamlit dashboard. Demonstrates cloud-native architecture, cost optimization (~$105/month), and production best practices."**

## Project Stats

- **Duration**: 1-2 weeks (for full implementation)
- **Languages**: Python, SQL, HCL (Terraform)
- **Frameworks**: FastAPI, PySpark, dbt, Streamlit, Airflow
- **Cloud Services**: 10+ GCP products
- **Infrastructure**: 100% IaC with Terraform
- **Testing**: Unit, integration, and E2E tests
- **Documentation**: 5,000+ words

## Contact

For questions or collaboration:
- **Email**: your.email@example.com
- **LinkedIn**: linkedin.com/in/yourname
- **Portfolio**: yourportfolio.com

---

**This project showcases production-ready data engineering skills suitable for senior-level roles at modern data-driven companies.**
