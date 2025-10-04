# Bangkok AQI Pipeline - Interview Cheat Sheet

## 🎯 30-Second Pitch
"I built an end-to-end data engineering pipeline that ingests Bangkok weather and air quality data from Open-Meteo APIs, transforms it through layered SQL models in DuckDB, and visualizes insights via Streamlit. It's production-ready with automated testing, proper documentation, and runs locally today."

## 📊 Quick Stats
- **Duration**: 1-day build | **Code**: 850 lines | **Tests**: 4 quality checks
- **Stack**: Python 3.13, DuckDB, Streamlit, pandas, SQL, Make
- **GitHub**: https://github.com/potangpa-sudo/bangkok-aqi-pipeline

## 🏗️ Architecture in 3 Lines
1. **Ingest**: Python fetches JSON from APIs → saves raw → normalizes with pandas
2. **Transform**: SQL layers (raw → staging → fact → mart) in DuckDB
3. **Serve**: Streamlit reads mart table → displays KPIs, charts, tables

## 💻 Technical Highlights
```python
# Idempotent upsert pattern
conn.execute("DELETE FROM table WHERE time IN (SELECT time FROM new_data)")
conn.execute("INSERT INTO table SELECT * FROM new_data")

# Timezone-aware processing
df['time'] = df['time'].dt.tz_localize('Asia/Bangkok')

# Layered SQL transformations
raw → staging (dedup) → fact (join) → mart (aggregate)
```

## 🐛 5 Problems Solved
1. **Git Auth**: Implemented SSH keys after password auth failed
2. **Timezone**: Explicit Bangkok UTC+7 handling to prevent date bucketing errors
3. **Idempotency**: Upsert pattern to prevent duplicates on reruns
4. **API Errors**: Added timeout + error handling for network resilience
5. **Git Hygiene**: Created .gitignore to exclude 2.5MB DuckDB file

## 🎓 Skills Demonstrated
**Technical**: Python (OOP, types), SQL (CTEs, joins, window functions), Data Modeling (Kimball), pandas, DuckDB, Streamlit, Git/SSH, Makefile
**Soft**: Problem-solving, Design thinking, Documentation, Independent delivery

## 💡 Architecture Decisions
| Choice | Why | Trade-off |
|--------|-----|-----------|
| DuckDB | OLAP-optimized, embedded, fast | Not for high-concurrency writes |
| SQL files | Simple, readable | Less powerful than dbt |
| Layered model | Clear separation, debuggable | Storage overhead |
| Makefile | Portable, no deps | Less robust than Airflow |

## 🚀 Next Steps (Show Growth Mindset)
**Short-term**: CI/CD (GitHub Actions), Official AQI formula, More tests
**Medium-term**: Docker, Airflow/Prefect, dbt migration
**Long-term**: Cloud deployment, Great Expectations, Multiple data sources

## 💬 Interview Q&A Quick Answers

**"Why DuckDB?"**
→ "OLAP-optimized for analytics, embedded (no server), columnar storage = fast aggregations. Perfect for read-heavy workloads."

**"How to scale to millions of records?"**
→ "Partition by date, incremental processing, migrate to Snowflake/BigQuery, add streaming (Kafka), implement retention policy."

**"How ensure data quality?"**
→ "Schema validation, deduplication, automated tests (existence/freshness/volume), null handling, audit trail via raw JSON. Next: Great Expectations."

**"What would you change?"**
→ "Use dbt (better testing), proper logging (structlog), retry logic with backoff, monitoring (Prometheus), Pydantic validation."

**"How handle security?"**
→ "No creds in code (env vars), SSH keys, read-only DB in dashboard, .gitignore. Production: Vault, encryption, RBAC, audit logs."

## 📸 2-Minute Demo Script
1. **GitHub** (15s): Show structure, README, commits
2. **Code** (30s): `cat src/config.py` + `cat sql/40_mart_daily_aqi_weather.sql`
3. **Run** (45s): `make run` (twice to show idempotency)
4. **Test** (15s): `make test`
5. **Dashboard** (15s): `make dashboard` → show visualizations

## 🎯 Closing Statement
"This project proves I can independently deliver end-to-end data solutions following industry best practices. I'm ready to contribute to production data engineering teams on day one."

---

## 📂 File Structure (Memorize This)
```
bangkok-aqi-pipeline/
├── src/                  # Python modules (config, ingest, load, pipeline, tests)
├── sql/                  # SQL transformations (00→10→11→20→30→40)
├── app/                  # Streamlit dashboard
├── data/
│   ├── raw/             # JSON audit trail
│   └── warehouse.duckdb # DuckDB file (gitignored)
├── Makefile             # Automation (setup, run, test, dashboard)
├── requirements.txt     # Pinned dependencies
└── README.md            # Full documentation
```

## 🔢 Metrics to Mention
- ⏱️ **5 seconds** per pipeline run (72 hours of data)
- 💾 **2.5 MB** DuckDB file (week of data)
- ✅ **100%** data completeness
- 🔄 **5 minute** dashboard cache TTL
- 📊 **3 KPIs** + **2 chart types** in dashboard

## 🏆 Standout Moments
1. "I encountered a Git authentication error and solved it by implementing SSH keys"
2. "Timezone handling was tricky—I learned to be explicit with tz_localize to avoid date bucket errors"
3. "I designed for idempotency from the start so the pipeline is safe to rerun"
4. "I followed Kimball methodology with clear raw/staging/fact/mart layers"
5. "I documented everything including this presentation guide for knowledge sharing"
