# Interview Preparation Checklist - Bangkok AQI Pipeline

## ✅ Pre-Interview Checklist (24 Hours Before)

### Technical Preparation
- [ ] Clone fresh copy of repo and verify it runs: `git clone && make setup && make run`
- [ ] Run all tests successfully: `make test`
- [ ] Launch dashboard and verify it loads: `make dashboard`
- [ ] Review all code files (can you explain every line?)
- [ ] Check GitHub repo is accessible and looks professional
- [ ] Prepare 2-minute demo script and practice 3 times
- [ ] Test screen sharing if remote interview

### Materials Preparation
- [ ] Print INTERVIEW_CHEATSHEET.md (one page reference)
- [ ] Read PRESENTATION.md thoroughly (full context)
- [ ] Review VISUAL_SUMMARY.md (quick reference diagrams)
- [ ] Review PRESENTATION_SLIDES.md (10-slide structure)
- [ ] Prepare laptop with all bookmarks ready
- [ ] Charge laptop + bring charger
- [ ] Test internet connection if remote
- [ ] Have backup (phone hotspot) if remote

### Mental Preparation
- [ ] Review the 5 problems you solved
- [ ] Practice 30-second elevator pitch
- [ ] Prepare 3 questions to ask them
- [ ] Get good sleep (7-8 hours)
- [ ] Eat well before interview
- [ ] Arrive/login 10 minutes early

---

## 🎯 30-Second Elevator Pitch (Memorize This)

> "I built an end-to-end data engineering pipeline that ingests Bangkok weather and air quality data from Open-Meteo APIs, transforms it through layered SQL models in DuckDB, and visualizes insights via Streamlit. The pipeline processes 72 hours of data in 5 seconds, includes automated quality testing, and follows data warehouse best practices with clear raw-staging-fact-mart layers. It's production-ready and demonstrates my ability to deliver complete data solutions independently."

---

## 💻 2-Minute Demo Script (Practice 3x)

### Setup (5 seconds)
```bash
cd bangkok-aqi-pipeline
ls -la  # Show structure
```
*"Let me show you the project structure. We have source code, SQL transformations, a dashboard app, and data storage."*

### Run Pipeline (30 seconds)
```bash
make run
```
*"I'll run the full pipeline. Watch as it fetches weather and air quality data from Open-Meteo APIs, saves raw JSON for audit trails, loads it into DuckDB, and executes SQL transformations through four layers: raw, staging, fact, and mart. The entire process takes about 5 seconds."*

### Show Code (25 seconds)
```bash
cat src/config.py | head -20
```
*"Here's my configuration management—using dataclasses and python-dotenv for clean env handling."*

```bash
cat sql/40_mart_daily_aqi_weather.sql
```
*"And here's the final mart layer SQL that aggregates hourly data to daily summaries."*

### Run Tests (20 seconds)
```bash
make test
```
*"The pipeline includes automated data quality tests that verify tables exist, contain data, and are fresh. All tests passing."*

### Show Dashboard (30 seconds)
```bash
make dashboard
# Browser opens to http://localhost:8502
```
*"Finally, the Streamlit dashboard provides KPI cards for latest metrics, trend charts showing PM2.5 and temperature over time, and a data table. The dashboard reads from DuckDB in read-only mode for safety."*

### Closing (10 seconds)
*"The entire project is on GitHub with comprehensive documentation. I encountered and solved 5 technical challenges during development, which I'm happy to discuss."*

---

## 🔥 Top 10 Questions You WILL Be Asked

### 1. "Walk me through your project."
**Answer:** Use the 30-second pitch, then expand to 2-minute demo.

**Key Points:**
- Start with problem statement
- Explain architecture flow
- Highlight technical choices
- Show results/metrics
- Mention challenges solved

### 2. "Why did you choose [DuckDB/Python/Streamlit]?"
**Answer:** "DuckDB is optimized for OLAP workloads with columnar storage, perfect for analytics. It's embedded so no server setup, incredibly fast for aggregations, and has excellent SQL support. Python is the lingua franca of data engineering with rich ecosystem. Streamlit enabled rapid dashboard development."

**Alternative if pressed:** "If we needed high-concurrency writes, I'd choose PostgreSQL. For enterprise scale, Snowflake or BigQuery. The principles remain the same—the key is choosing the right tool for the requirements."

### 3. "What was the most challenging part?"
**Answer:** "Timezone handling was surprisingly tricky. Bangkok is UTC+7, and I needed to ensure data landed in correct date buckets. I learned to be explicit with `tz_localize()` and test edge cases. It taught me that assumptions about time are dangerous in data pipelines."

**Follow-up ready:** Can explain the specific pandas code and how you tested it.

### 4. "How would you scale this to millions of records?"
**Answer:** "Several approaches:
1. **Partition by date** in DuckDB for query performance
2. **Incremental processing**—only fetch new data since last run
3. **Cloud warehouse migration** to Snowflake/BigQuery for massive scale
4. **Streaming architecture** with Kafka + Flink for real-time
5. **Data retention policy**—archive old data to cheaper storage like S3 Glacier
6. **Parallel processing** for multiple cities/sources"

### 5. "How do you ensure data quality?"
**Answer:** "Multi-layered approach:
1. **Schema validation** at ingestion (required fields present)
2. **Deduplication** in loading process (upsert pattern)
3. **Automated tests** after pipeline runs (existence, volume, freshness)
4. **Null handling** with explicit coercion and dropna where appropriate
5. **Audit trail** via raw JSON persistence
Next step would be Great Expectations for comprehensive validation rules."

### 6. "What would you do differently if you rebuilt this?"
**Answer:** "I'd:
1. Use **dbt** for SQL with built-in testing and documentation
2. Add **proper logging** (structlog) instead of prints
3. Implement **retry logic** with exponential backoff for API calls
4. Add **monitoring** (Prometheus/Grafana) for observability
5. Use **Pydantic models** for stronger type validation
6. **Separate** API clients into individual modules
These would make it more production-ready for team environments."

### 7. "Tell me about a problem you encountered."
**Answer:** Pick one of the 5 problems. Example:

**Git Authentication Failure:**
- "I initially tried pushing with HTTPS password, which GitHub deprecated in 2021"
- "Error was 'Password authentication is not supported'"
- "I generated SSH keys with `ssh-keygen -t ed25519`, added public key to GitHub, and updated remote to use SSH"
- "Learned to always use SSH or PAT tokens, and importance of staying current with security practices"

### 8. "How would you deploy this to production?"
**Answer:** "Production deployment would include:

**Infrastructure:**
- Containerize with Docker for reproducibility
- Deploy to cloud (AWS ECS/EKS or GCP Cloud Run)
- Separate compute (pipeline) from storage (database)

**Orchestration:**
- Migrate to Airflow/Prefect for scheduling
- Add retry logic and alerting
- Implement backfill capabilities

**Observability:**
- Structured logging to central system
- Metrics (pipeline duration, row counts)
- Alerts for failures or data quality issues

**Security:**
- Secrets management (Vault, AWS Secrets Manager)
- IAM roles, not credentials
- Network isolation

**CI/CD:**
- GitHub Actions for testing
- Automated deployments on merge to main
- Blue-green deployments for zero downtime"

### 9. "How do you handle errors and failures?"
**Answer:** "Current implementation:
- API calls have 30-second timeout
- Fail fast with clear error messages
- Raw JSON saved before processing (can replay)
- Tests validate pipeline outputs

**Production improvements:**
- Retry with exponential backoff for transient failures
- Dead letter queue for persistent failures
- Alerting (PagerDuty, Slack) for critical issues
- Circuit breaker pattern for external services
- Checkpointing for resume capability"

### 10. "Why should we hire you?"
**Answer:** "I've demonstrated I can:
1. **Deliver complete solutions** independently—this project went from zero to production-ready in one day
2. **Follow best practices**—layered architecture, testing, documentation
3. **Solve real problems**—I debugged 5 technical issues during development
4. **Learn quickly**—I researched and implemented tools I hadn't used before
5. **Think about maintainability**—clean code, clear structure, comprehensive docs

Most importantly, I'm passionate about data engineering and continuously learning. This project proves I can contribute value to your team from day one."

---

## 🎭 Behavioral Questions Prep

### "Tell me about yourself"
"I'm a data engineer with a passion for building robust, scalable pipelines. Most recently, I built an end-to-end ETL system for Bangkok air quality data that demonstrates my full-stack data engineering skills. Before that, [your background]. I'm excited about [company] because [research their work]."

### "Why do you want to work here?"
[Research company beforehand!]
- Mention specific products/technologies they use
- Reference their engineering blog posts
- Connect to your project: "I built with DuckDB, I see you use [similar tool]"
- Show enthusiasm for their mission

### "What's your greatest weakness?"
"I sometimes over-engineer solutions when simple would work. For example, in this project I initially planned complex error handling, but realized for this scope, fail-fast with clear messages was sufficient. I'm learning to balance perfection with pragmatism."

### "Where do you see yourself in 5 years?"
"I want to grow from individual contributor to tech lead, architecting complex data systems and mentoring junior engineers. I'm particularly interested in [streaming/ML/distributed systems] and want to deepen expertise there. This role seems like a great path toward that growth."

---

## 📋 Questions to Ask THEM

### About the Role
1. "What does a typical day look like for someone in this role?"
2. "What are the biggest data challenges the team is facing right now?"
3. "What tech stack do you use for data pipelines? How does my project align?"
4. "How do you handle data quality and observability?"
5. "What's the on-call rotation like?"

### About the Team
6. "Can you tell me about the team structure and who I'd be working with?"
7. "How does the team handle code reviews and knowledge sharing?"
8. "What does success look like in the first 30/60/90 days?"
9. "What opportunities are there for learning and growth?"

### About the Company
10. "What excites you most about working here?"
11. "How does the data team collaborate with other teams (ML, analytics, product)?"
12. "What's the company's approach to work-life balance?"

**Never ask:** Salary (wait for them), basic info on website, yes/no questions

---

## 🧠 Mental Models to Reference

### The Data Engineering Lifecycle (Fundamentals of Data Engineering)
Source → Ingestion → Storage → Transformation → Serving

*"My project implements this full lifecycle..."*

### Kimball Dimensional Modeling
Fact tables + dimension tables in star schema

*"I followed Kimball methodology with hourly fact table..."*

### Medallion Architecture (Databricks)
Bronze (raw) → Silver (refined) → Gold (aggregated)

*"My raw/staging/fact/mart layers mirror medallion architecture..."*

### CAP Theorem
Consistency, Availability, Partition tolerance—pick 2

*"DuckDB prioritizes consistency and availability since it's single-node..."*

---

## ⚠️ Common Mistakes to AVOID

### Technical Mistakes
- ❌ Overpromising on skills you don't have
- ❌ Badmouthing previous employers/technologies
- ❌ Getting defensive about limitations
- ❌ Using jargon without explaining
- ❌ Not admitting when you don't know something

### Presentation Mistakes
- ❌ Going over time limit
- ❌ Technical difficulties during demo (TEST BEFOREHAND!)
- ❌ Reading from slides verbatim
- ❌ Monotone delivery
- ❌ Not making eye contact

### Behavioral Mistakes
- ❌ Arriving late
- ❌ Dressing inappropriately
- ❌ Checking phone during interview
- ❌ Not asking any questions
- ❌ Appearing disinterested or arrogant

---

## 🎯 Success Indicators

**You're doing well if:**
- ✅ Interviewer is engaged and asking follow-up questions
- ✅ They're taking notes
- ✅ Discussion goes beyond prepared material
- ✅ They share details about the team/company
- ✅ They ask about your availability/timeline
- ✅ Interview goes over scheduled time (in a good way)
- ✅ They introduce you to other team members
- ✅ You feel natural chemistry/rapport

**Red flags to notice:**
- 🚩 Interviewer seems distracted or disengaged
- 🚩 Very short interview (if scheduled for 1hr, ends in 20min)
- 🚩 No opportunity for questions
- 🚩 Vague or evasive answers to your questions
- 🚩 No mention of next steps
- 🚩 Negative comments about team/company

---

## 📞 Post-Interview Follow-Up

### Within 24 Hours: Send Thank You Email

**Template:**

```
Subject: Thank you - [Your Name] - [Position] Interview

Dear [Interviewer Name],

Thank you for taking the time to speak with me today about the [Position] 
role at [Company]. I enjoyed learning about [specific topic discussed] and 
discussing my Bangkok AQI Pipeline project with you.

I was particularly excited to hear about [something specific they mentioned]. 
The challenge of [problem they mentioned] aligns well with my experience in 
[relevant skill from your project].

I'm confident my skills in Python, SQL, and data pipeline development would 
enable me to contribute to your team immediately. I'm very interested in the 
opportunity and look forward to hearing about next steps.

Thank you again for your consideration.

Best regards,
[Your Name]
[LinkedIn Profile]
[GitHub: github.com/potangpa-sudo/bangkok-aqi-pipeline]
```

### Day 3-5: Follow Up if No Response
Polite check-in asking about timeline.

### Day 7-10: Assume No Interest
Move on to other opportunities, but keep door open.

---

## 🎊 Final Confidence Boosters

**Remember:**
1. **You built something real** that works
2. **You solved real problems** and documented them
3. **You learned valuable skills** in the process
4. **You can explain your choices** rationally
5. **You're ready for this role**

**If you get nervous:**
- Take deep breaths
- Smile (releases endorphins)
- Remember: they're rooting for you to succeed
- It's a conversation, not an interrogation
- Worst case: you gain interview experience

**You've got this!** 🚀

---

## 📚 Day-Before Review Checklist

**The Night Before:**
- [ ] Review this checklist one final time
- [ ] Practice 30-second pitch 3 times
- [ ] Run through 2-minute demo once
- [ ] Review top 10 questions
- [ ] Prepare your outfit
- [ ] Set 2 alarms
- [ ] Go to bed early

**Morning Of:**
- [ ] Eat a good breakfast
- [ ] Test your tech (camera, mic, screen share)
- [ ] Have water nearby
- [ ] Dress professionally
- [ ] Arrive/login 10 minutes early
- [ ] Take 3 deep breaths
- [ ] Smile and be yourself

**During Interview:**
- [ ] Make eye contact
- [ ] Speak clearly and confidently
- [ ] Show enthusiasm
- [ ] Listen actively
- [ ] Ask clarifying questions
- [ ] Take notes
- [ ] Thank them at the end

---

**You're prepared. You're capable. You're ready. Go show them what you've built!** 💪

Good luck! 🍀
