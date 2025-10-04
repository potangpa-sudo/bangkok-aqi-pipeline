# GitHub Repository Setup Guide

This guide helps you configure optimal settings for the Bangkok AQI Pipeline repository.

## 📋 Repository Settings Checklist

### General Settings

**Repository Details**
- [x] Add description: "Production-grade data engineering pipeline for Bangkok air quality monitoring using GCP, Terraform, Airflow, dbt, and Streamlit"
- [x] Add website: Your deployed dashboard URL
- [x] Add topics: `data-engineering`, `gcp`, `terraform`, `airflow`, `dbt`, `streamlit`, `bigquery`, `data-pipeline`, `air-quality`, `bangkok`, `python`, `cloud-run`, `dataproc`, `spark`

**Features**
- [x] ✅ Wikis - Enable for additional documentation
- [x] ✅ Issues - Enable for bug tracking
- [x] ✅ Sponsorships - Enable if you want to accept donations
- [x] ✅ Projects - Enable for project management
- [x] ✅ Discussions - Enable for community Q&A
- [x] ❌ Restrict editing to collaborators

**Pull Requests**
- [x] ✅ Allow merge commits
- [x] ✅ Allow squash merging (Default)
- [x] ✅ Allow rebase merging
- [x] ✅ Always suggest updating pull request branches
- [x] ✅ Automatically delete head branches

**Archives**
- [x] ❌ Include Git LFS objects in archives

### Branch Protection Rules

Create a rule for `main` branch:

**Branch name pattern**: `main`

**Protect matching branches**
- [x] ✅ Require a pull request before merging
  - [x] Required approvals: 1
  - [x] ✅ Dismiss stale pull request approvals when new commits are pushed
  - [x] ✅ Require review from Code Owners
- [x] ✅ Require status checks to pass before merging
  - [x] ✅ Require branches to be up to date before merging
  - Required status checks:
    - [x] `lint-python`
    - [x] `test-python`
    - [x] `validate-terraform`
    - [x] `validate-dbt`
- [x] ✅ Require conversation resolution before merging
- [x] ✅ Require signed commits
- [x] ✅ Require linear history
- [x] ❌ Include administrators (uncheck during initial setup)
- [x] ✅ Restrict who can push to matching branches
- [x] ✅ Allow force pushes (❌ Keep disabled)
- [x] ✅ Allow deletions (❌ Keep disabled)

### Code Security and Analysis

**Dependency Graph**
- [x] ✅ Enable (automatically enabled for public repos)

**Dependabot**
- [x] ✅ Dependabot alerts
- [x] ✅ Dependabot security updates
- [x] ✅ Dependabot version updates

Create `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    reviewers:
      - "potangpa-sudo"
  
  - package-ecosystem: "terraform"
    directory: "/infra/terraform"
    schedule:
      interval: "weekly"
    reviewers:
      - "potangpa-sudo"
  
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    reviewers:
      - "potangpa-sudo"
```

**Code Scanning**
- [x] ✅ CodeQL analysis
  - Setup: Default
  - Languages: Python
  - Query suites: Default

**Secret Scanning**
- [x] ✅ Secret scanning (automatically enabled for public repos)
- [x] ✅ Push protection

### Actions

**General**
- [x] ✅ Allow all actions and reusable workflows
- [x] ✅ Allow actions created by GitHub
- [x] ✅ Allow actions by Marketplace verified creators

**Workflow Permissions**
- [x] 🔘 Read and write permissions
- [x] ✅ Allow GitHub Actions to create and approve pull requests

**Required Workflows**
- None (optional: add organization-wide workflows)

### Pages

**Source**
- Branch: `gh-pages` (will be created by release workflow)
- Folder: `/` (root)

**Custom Domain** (Optional)
- Add your custom domain if available
- [x] ✅ Enforce HTTPS

### Environments

Create environments for deployment:

**1. Development**
- Wait timer: 0 minutes
- Required reviewers: None
- Deployment branches: All branches

**2. Staging**
- Wait timer: 0 minutes
- Required reviewers: 1 (yourself)
- Deployment branches: `main`, `develop`

**3. Production**
- Wait timer: 5 minutes
- Required reviewers: 1 (yourself)
- Deployment branches: `main` only
- Environment secrets:
  - `GCP_PROJECT_ID`
  - `GCP_SA_KEY`
  - `GCS_BUCKET_RAW`
  - `GCS_BUCKET_QUAR`

### Secrets and Variables

**Repository Secrets** (Settings → Secrets and variables → Actions)

Add these secrets:
```
GCP_PROJECT_ID        → Your GCP project ID
GCP_SA_KEY            → Service account JSON key (for CI/CD)
GCS_BUCKET_RAW        → Raw data bucket name
GCS_BUCKET_QUAR       → Quarantine bucket name
SLACK_WEBHOOK_URL     → (Optional) Slack notifications
```

**Repository Variables**

Add these variables:
```
GCP_REGION           → asia-southeast1
TERRAFORM_VERSION    → 1.5.0
PYTHON_VERSION       → 3.11
NODE_VERSION         → 18
```

### Webhooks

**Optional Integrations**

Add webhooks for:
- Slack notifications
- Discord notifications
- Project management tools
- CI/CD platforms

### Collaborators

**Add Team Members**

1. Go to Settings → Collaborators and teams
2. Add collaborators with appropriate roles:
   - **Admin**: Full access
   - **Write**: Push, create branches
   - **Triage**: Manage issues and PRs
   - **Read**: View and clone

### Labels

**Default Labels** - Keep these:
- `bug` - Something isn't working
- `documentation` - Documentation improvements
- `duplicate` - Duplicate issue
- `enhancement` - New feature or request
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `invalid` - Doesn't seem right
- `question` - Further information requested
- `wontfix` - Won't be fixed

**Custom Labels** - Add these:

```
Priority:
priority: critical     #d73a4a
priority: high         #ff9800
priority: medium       #ffc107
priority: low          #4caf50

Type:
type: feature          #0052cc
type: bug              #d73a4a
type: docs             #1d76db
type: refactor         #fbca04
type: test             #6f42c1

Component:
component: terraform   #844fba
component: airflow     #00ad46
component: dbt         #ff6849
component: spark       #e25a1c
component: dashboard   #1e88e5
component: ingestor    #0d7d9f

Status:
status: blocked        #b60205
status: in progress    #fbca04
status: needs review   #0052cc
status: ready          #0e8a16
```

### Milestones

Create milestones for tracking progress:

**v1.1 - Multi-City Support**
- Due date: Q4 2025
- Description: Add support for multiple cities beyond Bangkok

**v1.2 - Real-time Streaming**
- Due date: Q1 2026
- Description: Implement real-time data streaming pipeline

**v2.0 - ML Predictions**
- Due date: Q2 2026
- Description: Add ML-based AQI forecasting

### Projects

**Create a Project Board**

1. Go to Projects → New project
2. Choose template: "Team backlog"
3. Name: "Bangkok AQI Pipeline Roadmap"
4. Views:
   - **Board**: Kanban-style board
   - **Table**: Detailed list view
   - **Roadmap**: Timeline view

**Columns**:
- 📋 Backlog
- 🔍 Triage
- 📝 Todo
- 🚧 In Progress
- 👀 In Review
- ✅ Done

### Discussions

**Enable Categories**:
- 💬 General
- 💡 Ideas
- ❓ Q&A
- 🙏 Show and tell
- 📢 Announcements

**Pin Important Discussions**:
- Welcome & Guidelines
- Roadmap Discussion
- FAQ

### Insights

**Enable useful insights**:
- [x] Pulse - Activity overview
- [x] Contributors - Top contributors
- [x] Community - Community standards checklist
- [x] Traffic - Views and clones
- [x] Commits - Commit activity
- [x] Code frequency - Additions and deletions
- [x] Dependency graph - Dependencies
- [x] Network - Fork relationships

## 🔧 Maintenance Tasks

### Weekly
- [ ] Review and respond to issues
- [ ] Review pull requests
- [ ] Check CI/CD status
- [ ] Update dependencies (if Dependabot PRs)

### Monthly
- [ ] Review and update documentation
- [ ] Check and respond to discussions
- [ ] Review security alerts
- [ ] Update project roadmap

### Quarterly
- [ ] Major version planning
- [ ] Community recognition
- [ ] Infrastructure cost review
- [ ] Performance optimization

## 📱 GitHub Mobile

Install GitHub Mobile app for:
- Quick issue triage
- PR reviews on-the-go
- Notifications management
- Repository browsing

## 🔔 Notification Settings

**Recommended Settings**:

**Watching**
- [x] All Activity - For your repository
- [x] Custom - For others' repositories

**Participating and @mentions**
- [x] ✅ Enable notifications

**Email Preferences**
- [x] Comments on Issues and Pull Requests
- [x] Pull Request reviews
- [x] Pull Request pushes
- [x] Your Dependabot alerts

## 🎯 Community Standards

Check your progress at:
`https://github.com/potangpa-sudo/bangkok-aqi-pipeline/community`

Complete checklist:
- [x] ✅ Description
- [x] ✅ README
- [x] ✅ Code of conduct
- [x] ✅ Contributing guide
- [x] ✅ License
- [x] ✅ Security policy
- [x] ✅ Issue templates
- [x] ✅ Pull request template

## 📊 Badges to Add

Add these to your README for visibility:

```markdown
[![GitHub stars](https://img.shields.io/github/stars/potangpa-sudo/bangkok-aqi-pipeline?style=social)](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/potangpa-sudo/bangkok-aqi-pipeline?style=social)](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/network/members)
[![GitHub issues](https://img.shields.io/github/issues/potangpa-sudo/bangkok-aqi-pipeline)](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/potangpa-sudo/bangkok-aqi-pipeline)](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/pulls)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CodeQL](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/workflows/CodeQL/badge.svg)](https://github.com/potangpa-sudo/bangkok-aqi-pipeline/actions/workflows/codeql.yml)
```

## 🚀 Post-Setup Checklist

After configuring all settings:

- [ ] Test CI/CD pipeline
- [ ] Create first issue
- [ ] Create project board
- [ ] Enable discussions
- [ ] Invite collaborators
- [ ] Set up webhooks
- [ ] Configure branch protection
- [ ] Test PR workflow
- [ ] Verify secrets are set
- [ ] Enable Dependabot
- [ ] Configure CodeQL
- [ ] Set up GitHub Pages
- [ ] Create first release
- [ ] Pin repository
- [ ] Update profile README to link to project

## 🎉 You're All Set!

Your repository is now professionally configured and ready for collaboration!

**Share your project**:
- Post on LinkedIn
- Share on Twitter/X
- Add to your portfolio
- Submit to awesome lists
- Present at meetups

---

Need help? Check the [GitHub Documentation](https://docs.github.com/) or open a discussion!
