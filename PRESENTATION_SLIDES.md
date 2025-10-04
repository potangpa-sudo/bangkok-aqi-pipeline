# Bangkok AQI Pipeline - Slide Deck Outline

## 🎯 Presentation Structure (10 slides, 5 minutes)

---

### SLIDE 1: Title Slide
**Bangkok AQI Pipeline**
End-to-End Data Engineering Portfolio Project

*Your Name*  
GitHub: github.com/potangpa-sudo/bangkok-aqi-pipeline

**Visual**: Project logo or Bangkok skyline with air quality overlay

---

### SLIDE 2: Problem Statement
**The Challenge**
- Bangkok faces serious air quality issues (PM2.5 often exceeds safe levels)
- Data is scattered across multiple sources
- No integrated view of weather + air quality correlation
- Need: Real-time monitoring + historical trend analysis

**What I Built**
- Automated ETL pipeline ingesting data hourly
- Analytics-ready data warehouse with proper modeling
- Interactive dashboard for insights

**Visual**: Before/After diagram (scattered data → unified dashboard)

---

### SLIDE 3: Architecture Overview
```
Open-Meteo APIs (Weather + AQ)
        ↓
Python Ingestion Layer
        ↓
DuckDB Warehouse (Layered)
  - Raw Layer
  - Staging Layer
  - Fact Layer
  - Mart Layer
        ↓
Streamlit Dashboard
```

**Tech Stack**
- Python 3.13 • DuckDB • Streamlit • pandas • SQL • Make

**Visual**: Architecture flowchart with technology icons

---

### SLIDE 4: Data Flow & Layering
**Medallion Architecture Implementation**

```
┌─────────────────────────────────────────┐
│ RAW: Unprocessed API responses         │
│ raw.raw_weather, raw.raw_air_quality   │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ STAGING: Cleaned & deduplicated         │
│ stg.stg_weather, stg.stg_air_quality   │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ FACT: Joined hourly observations        │
│ fct.aqi_by_hour                         │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ MART: Daily aggregates for analysis     │
│ mart.daily_aqi_weather                  │
└─────────────────────────────────────────┘
```

**Visual**: Layered pyramid diagram with data flow arrows

---

### SLIDE 5: Key Technical Implementations

**1. Idempotent Data Loading**
```python
DELETE FROM table WHERE time IN (SELECT time FROM new_data)
INSERT INTO table SELECT * FROM new_data
```
✅ Safe to rerun | ✅ Handles backfills

**2. Timezone-Aware Processing**
```python
df['time'] = df['time'].dt.tz_localize('Asia/Bangkok')
```
✅ Accurate date bucketing | ✅ DST handling

**3. SQL Transformations**
- Window functions for deduplication
- CTEs for readability
- Proper grain management

**Visual**: Code snippets with checkmarks

---

### SLIDE 6: Problems Solved
| Problem | Solution | Learning |
|---------|----------|----------|
| **Git Auth Failure** | Implemented SSH keys | Security best practices |
| **Timezone Bugs** | Explicit tz handling | Be explicit with time |
| **Duplicate Data** | Upsert pattern | Design for idempotency |
| **API Failures** | Timeout + error handling | External deps are fragile |
| **Large Files in Git** | .gitignore setup | Repo hygiene matters |

**Visual**: Problem → Solution → Learning flowchart

---

### SLIDE 7: Data Quality & Testing
**Testing Strategy**

✅ **Schema Tests**
- Required tables exist
- Correct column types

✅ **Volume Tests**
- Non-empty tables
- Expected row counts

✅ **Freshness Tests**
- Data within 3 days
- No stale data

✅ **Integrity Tests**
- No nulls in critical columns
- Valid value ranges

**Results**: 100% test pass rate

**Visual**: Testing pyramid or checklist with green checkmarks

---

### SLIDE 8: Dashboard Demo
**Key Features**

📊 **KPI Cards**
- Latest Avg PM2.5: 12.1 µg/m³
- Latest Avg Temp: 27.7°C
- Latest Humidity: 84.2%

📈 **Trend Charts**
- PM2.5 & Temperature over time
- AQI Proxy by day (bar chart)

📋 **Data Table**
- Recent daily observations
- Filterable and sortable

**Visual**: Dashboard screenshot with callouts

---

### SLIDE 9: Results & Impact
**Metrics Achieved**

⚡ **Performance**
- 5 seconds per pipeline run
- 2.5 MB storage for week of data
- Sub-second dashboard load time

📊 **Data Quality**
- 100% completeness
- Real-time freshness
- Zero data loss

🛠️ **Developer Experience**
- Single command deployment: `make run`
- Automated testing: `make test`
- Interactive exploration: `make dashboard`

**Visual**: Metrics dashboard with numbers and icons

---

### SLIDE 10: Next Steps & Vision
**Immediate Improvements**
- CI/CD with GitHub Actions
- Official Thailand AQI formula
- Comprehensive unit tests

**Medium-term Goals**
- Docker containerization
- Airflow/Prefect orchestration
- dbt migration for SQL

**Long-term Vision**
- Cloud deployment (AWS/GCP)
- Multiple data sources (traffic, health)
- Machine learning predictions
- Public API for data access

**Call to Action**
*"Ready to bring these data engineering skills to your team!"*

**Visual**: Roadmap timeline

---

## 🎤 Speaker Notes

### Opening (30 seconds)
"Good [morning/afternoon], I'm excited to share a data engineering project I built from scratch. Over the course of one day, I created an end-to-end pipeline that solves a real problem: monitoring Bangkok's air quality. Let me walk you through the architecture, technical challenges, and what I learned."

### Architecture Section (1 minute)
"I followed a layered approach inspired by data warehousing best practices. Data flows from Open-Meteo APIs through Python ingestion, gets transformed through four SQL layers in DuckDB, and surfaces in a Streamlit dashboard. Each layer has a clear purpose: raw for audit trails, staging for cleaning, fact for analysis, and mart for consumption."

### Technical Challenges (1 minute)
"I encountered five significant problems during development. The most interesting was timezone handling—Bangkok is UTC+7, and getting date boundaries correct required explicit timezone localization. I also implemented an upsert pattern to ensure the pipeline is idempotent, meaning it's safe to rerun without creating duplicates."

### Results & Demo (1.5 minutes)
"The results speak for themselves: the pipeline processes 72 hours of data in just 5 seconds, all tests pass automatically, and the dashboard provides real-time insights. Let me show you a quick demo..." [Run through demo script]

### Closing (1 minute)
"This project demonstrates my ability to deliver end-to-end data solutions independently. I understand data modeling, write production-quality code, and follow best practices for testing and documentation. More importantly, I know what I don't know—I've already identified next steps like CI/CD, containerization, and migration to enterprise tools like Airflow and dbt. I'm ready to contribute to your data engineering team from day one."

---

## 📋 Pre-Presentation Checklist

**Technical Setup**
- [ ] Laptop fully charged
- [ ] Demo environment tested (run `make run && make test`)
- [ ] Dashboard running (`make dashboard`)
- [ ] Browser bookmarked to GitHub repo
- [ ] VS Code open with project
- [ ] Terminal ready with commands

**Materials**
- [ ] This presentation guide printed
- [ ] Cheat sheet on phone/tablet
- [ ] Business cards ready
- [ ] Resume with project highlighted

**Practice**
- [ ] Run through slides 3 times
- [ ] Demo script practiced
- [ ] Answers to common questions rehearsed
- [ ] 5-minute timing confirmed

---

## 🎭 Body Language & Delivery Tips

**Voice**
- Speak clearly and confidently
- Vary pace (slow for architecture, faster for familiar concepts)
- Pause after key points
- Show enthusiasm for problem-solving

**Gestures**
- Point to architecture diagrams when explaining flow
- Use hands to show "layering" concept
- Lean forward when discussing challenges (shows engagement)
- Maintain eye contact with interviewers

**Energy**
- Start strong with confident opening
- Build excitement during demo
- Show pride in problem-solving section
- Close with forward-looking vision

---

## ❓ Anticipated Questions & Answers

**Q: How long did this take you?**
A: "About one full day from planning to deployment. I spent the morning designing the architecture, afternoon implementing, and evening testing and documenting. The clear structure made development fast."

**Q: Have you worked with [other tool] before?**
A: "Not yet, but I learn quickly. I chose this stack because it's modern and relevant, but I understand the principles apply across tools. For example, my layered SQL approach would translate directly to dbt, and my pipeline structure would map well to Airflow DAGs."

**Q: What was the hardest part?**
A: "Timezone handling was surprisingly tricky. Bangkok is UTC+7, and I needed to ensure data landed in the correct date buckets. I learned to be explicit with timezone localization and test around edge cases. It taught me that assumptions about time are dangerous in data pipelines."

**Q: How would you handle this in production?**
A: "I'd add several things: proper logging with structured logs, monitoring and alerting for pipeline failures, secrets management for credentials, CI/CD for automated testing, and probably migrate orchestration to Airflow. I'd also add data quality checks with Great Expectations and implement a proper on-call rotation."

**Q: Why should we hire you?**
A: "I've demonstrated I can build end-to-end data solutions independently, following best practices. I document my work, test my code, and think about maintainability. Most importantly, I love solving data problems and continuously learning. This project is proof I can deliver value quickly while maintaining quality."

---

## 🎯 Success Metrics

**You know the presentation went well if:**
- ✅ You finished within 5 minutes
- ✅ Demo worked without technical issues
- ✅ Interviewers asked follow-up questions
- ✅ You confidently answered all questions
- ✅ You showed enthusiasm and passion
- ✅ You connected project to job requirements
- ✅ You asked thoughtful questions back

**Red flags to avoid:**
- ❌ Going over time limit
- ❌ Technical difficulties during demo
- ❌ Reading from slides verbatim
- ❌ Using jargon without explaining
- ❌ Getting defensive about limitations
- ❌ Not preparing for follow-up questions

---

Good luck with your interview! 🚀

Remember: **You built something real. You solved real problems. You learned from challenges. You're ready.**
