# GitHub Actions Setup Guide

This guide explains how to fix the failing GitHub Actions workflows and get your CI/CD pipelines working.

## Current Status

After pushing the code, you may see:
- ❌ **CI workflow**: May fail initially due to missing dependencies
- ❌ **Deploy workflow**: Skipped (requires secrets and manual trigger)

## Quick Fix

The workflows are now configured to:
1. **CI workflow** - Runs automatically on every push/PR and should pass
2. **Deploy workflow** - Only runs when manually triggered or when commit message contains `[deploy]`

## Why Were They Failing?

### 1. Missing Test Directory
**Fixed!** ✅ I added a `tests/` directory with basic tests.

### 2. Missing GCP Secrets
**Status**: The deploy workflow now gracefully skips when secrets aren't configured.

### 3. Deploy Workflow Runs Automatically
**Fixed!** ✅ Changed to manual trigger only.

## How to Fix the CI Badge (Make it Green)

The CI workflow should now pass automatically. If it's still failing, wait 2-3 minutes for GitHub Actions to complete.

### If CI is Still Failing:

1. Go to your repository: https://github.com/potangpa-sudo/bangkok-aqi-pipeline
2. Click on **Actions** tab
3. Find the failed workflow run
4. Click on it to see details
5. Check which job failed and why

Common issues:
- **Terraform fmt check**: Run `terraform fmt -recursive` in `infra/terraform/`
- **Python linting**: Run `ruff check --fix .` to auto-fix issues
- **Docker build**: Make sure Dockerfiles are valid

## How to Set Up Deployment (Optional)

The deploy workflow will only run when you're ready to deploy to GCP. Here's how to enable it:

### Step 1: Create GCP Service Account

```bash
# In your GCP project
gcloud iam service-accounts create github-actions \
    --display-name="GitHub Actions Deploy"

# Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/editor"

# Create and download key
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### Step 2: Add GitHub Secrets

1. Go to: https://github.com/potangpa-sudo/bangkok-aqi-pipeline/settings/secrets/actions
2. Click **New repository secret**
3. Add these secrets:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `GCP_PROJECT_ID` | Your GCP project ID | `my-project-123` |
| `GCP_SA_KEY` | Contents of `github-actions-key.json` | `{ "type": "service_account", ... }` |
| `GCS_BUCKET_RAW` | Raw data bucket name | `my-project-aqi-raw` |
| `GCS_BUCKET_QUAR` | Quarantine bucket name | `my-project-aqi-quarantine` |

### Step 3: Deploy Manually

Once secrets are set:

1. Go to **Actions** tab
2. Click on **Deploy to GCP** workflow
3. Click **Run workflow** button
4. Click **Run workflow** to confirm

OR

Make a commit with `[deploy]` in the message:
```bash
git commit --allow-empty -m "chore: trigger deployment [deploy]"
git push
```

## Understanding the Workflows

### CI Workflow (`.github/workflows/ci.yml`)

Runs on every push and PR. Checks:
- ✅ Python code linting with Ruff
- ✅ Type checking with mypy
- ✅ Python tests with pytest
- ✅ Terraform validation
- ✅ dbt compilation
- ✅ SQL linting (continues on error)
- ✅ Docker image builds

**This should pass without any setup!**

### Deploy Workflow (`.github/workflows/deploy.yml`)

Only runs when:
- You manually trigger it, OR
- Commit message contains `[deploy]`

Checks for secrets and skips gracefully if not configured.

Deployment jobs:
1. 📋 Terraform Plan
2. ✅ Terraform Apply (requires manual approval)
3. 🚀 Build & Deploy Ingestor to Cloud Run
4. 📊 Build & Deploy Dashboard to Cloud Run
5. ⚡ Upload Spark Job to GCS
6. 🔄 Run dbt Models
7. 🧪 Smoke Tests

### Release Workflow (`.github/workflows/release.yml`)

Runs when you create a git tag:
```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

This will:
- Create a GitHub Release
- Build and push Docker images to GHCR
- Package Terraform modules
- Generate documentation

## Troubleshooting

### CI Badge Shows "Failing"

**Wait 2-3 minutes** for the new workflow run to complete after pushing the fix.

If still failing:
1. Check the Actions tab for error details
2. Common fixes:
   ```bash
   # Format Terraform
   cd infra/terraform && terraform fmt -recursive
   
   # Fix Python linting
   ruff check --fix .
   
   # Run tests locally
   pytest tests/
   ```

### Deploy Badge Shows "Failing"

This is expected! The deploy workflow now only runs manually or with `[deploy]` in commit message.

The badge will show:
- ⚪ **No status** or **Skipped** - Normal, no deployment triggered
- ❌ **Failing** - Only if you triggered deployment and it failed
- ✅ **Passing** - Deployment succeeded

### "Context access might be invalid" Warnings

These are just VS Code warnings about secrets not being set. They don't affect workflow execution. GitHub Actions will handle missing secrets gracefully.

## Best Practices

### For Regular Development

```bash
# Make changes
git add .
git commit -m "feat: add new feature"
git push
```

This will:
- ✅ Run CI checks
- ❌ NOT deploy to GCP

### When Ready to Deploy

```bash
git commit -m "feat: add new feature [deploy]"
git push
```

OR use the Actions UI to manually trigger.

### For Releases

```bash
# Update CHANGELOG.md with new version
git add CHANGELOG.md
git commit -m "chore: prepare v1.1.0 release"
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin main --tags
```

This will trigger the release workflow.

## Summary

✅ **CI is now fixed** - Should pass automatically  
✅ **Deploy is now safe** - Won't fail without secrets  
✅ **Tests added** - Basic test suite included  
✅ **Workflows optimized** - Only run when needed  

Your badges should turn green within a few minutes! 🎉

---

**Need help?** Open an issue or check the [GitHub Actions documentation](https://docs.github.com/en/actions).
