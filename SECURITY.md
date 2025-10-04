# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

The Bangkok AQI Pipeline team takes security seriously. We appreciate your efforts to responsibly disclose your findings.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via:

1. **GitHub Security Advisories** (Preferred)
   - Navigate to the Security tab
   - Click "Report a vulnerability"
   - Fill out the form with details

2. **Email** (Alternative)
   - Send an email to: [INSERT YOUR SECURITY EMAIL]
   - Include "SECURITY" in the subject line

### What to Include

Please include the following information:

- **Description**: A clear description of the vulnerability
- **Impact**: What kind of impact the vulnerability has
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Affected Components**: Which parts of the system are affected
- **Proof of Concept**: Code snippets or screenshots if applicable
- **Suggested Fix**: If you have ideas on how to fix it

### Example Report

```
Subject: SECURITY - SQL Injection in Dashboard

Description:
SQL injection vulnerability in the dashboard component when filtering by date range.

Impact:
Attacker could potentially access unauthorized data or modify database contents.

Steps to Reproduce:
1. Access dashboard at /dashboard
2. Enter `' OR '1'='1` in the date filter
3. Submit the form
4. Observe unauthorized data access

Affected Components:
- app/dashboard_bq.py, line 45
- BigQuery query construction

Suggested Fix:
Use parameterized queries instead of string concatenation
```

## Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 1-7 days
  - High: 7-30 days
  - Medium: 30-90 days
  - Low: 90+ days

## Security Best Practices

### For Contributors

When contributing to this project, please follow these security practices:

#### 1. Secret Management
- **Never commit secrets** (API keys, passwords, tokens)
- Use `.env` files and add them to `.gitignore`
- Use GCP Secret Manager for production secrets
- Rotate credentials regularly

```bash
# Good - Use environment variables
PROJECT_ID = os.getenv("GCP_PROJECT_ID")

# Bad - Hardcoded secrets
PROJECT_ID = "my-project-123"
```

#### 2. Input Validation
- Always validate and sanitize user inputs
- Use Pydantic models for API request validation
- Implement proper error handling

```python
# Good - Validated input
from pydantic import BaseModel, validator

class CityRequest(BaseModel):
    city: str
    
    @validator('city')
    def validate_city(cls, v):
        if not v.isalpha():
            raise ValueError("City must contain only letters")
        return v

# Bad - No validation
city = request.args.get('city')  # Could be anything!
```

#### 3. SQL Injection Prevention
- Use parameterized queries
- Never concatenate user input into SQL
- Use ORM or query builders when possible

```python
# Good - Parameterized query
query = f"""
SELECT * FROM {dataset}.{table}
WHERE date = @date_param
"""
job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("date_param", "STRING", date)
    ]
)

# Bad - String concatenation
query = f"SELECT * FROM table WHERE date = '{date}'"  # Vulnerable!
```

#### 4. Authentication & Authorization
- Implement proper authentication for APIs
- Use least privilege principle for service accounts
- Validate JWT tokens properly
- Implement rate limiting

```python
# Good - Token validation
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    # Validate token properly
    if not is_valid_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
```

#### 5. Dependency Management
- Keep dependencies up to date
- Use `pip-audit` to scan for vulnerabilities
- Review security advisories for dependencies
- Pin dependency versions in production

```bash
# Check for vulnerabilities
pip install pip-audit
pip-audit

# Update dependencies
pip list --outdated
pip install --upgrade package-name
```

#### 6. Data Protection
- Encrypt sensitive data at rest and in transit
- Use HTTPS for all API communications
- Implement proper access controls
- Sanitize logs (no PII or secrets)

```python
# Good - Sanitized logging
logger.info(f"Processing data for city: {city}")

# Bad - Logging sensitive data
logger.info(f"API key: {api_key}")  # Never do this!
```

#### 7. Error Handling
- Don't expose internal details in error messages
- Log errors properly for debugging
- Return generic error messages to users

```python
# Good - Generic error message
try:
    process_data()
except Exception as e:
    logger.error(f"Data processing failed: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Processing failed")

# Bad - Exposing internals
except Exception as e:
    return {"error": str(e)}  # Could expose sensitive info!
```

### For Deployment

#### 1. Infrastructure Security
- Enable VPC Service Controls
- Use Private Google Access
- Implement network policies
- Enable Cloud Armor for DDoS protection

#### 2. IAM Best Practices
- Use service accounts with minimal permissions
- Enable workload identity for GKE
- Implement IAM conditions
- Regular IAM audits

#### 3. Monitoring & Alerting
- Enable Cloud Security Command Center
- Set up alerts for suspicious activity
- Monitor access logs
- Implement SIEM if applicable

#### 4. Compliance
- Follow data residency requirements
- Implement data retention policies
- Regular security audits
- GDPR/CCPA compliance if applicable

## Known Security Considerations

### Current Security Measures

1. **Service Accounts**: Least privilege IAM roles
2. **Secret Management**: GCP Secret Manager integration
3. **Data Encryption**: GCS and BigQuery default encryption
4. **Network Security**: Cloud Run with authentication
5. **Input Validation**: Pydantic models for API validation

### Potential Security Risks

1. **Public Cloud Run Services**: Consider implementing authentication
2. **Data Access**: Implement fine-grained access controls
3. **Logging**: Ensure no PII is logged
4. **Rate Limiting**: Implement API rate limiting

## Security Updates

Security patches will be released as needed. Subscribe to:
- GitHub Security Advisories
- GitHub Watch → Custom → Security alerts

## Acknowledgments

We appreciate the security research community. Contributors who report valid security issues will be:
- Acknowledged in the CHANGELOG (unless they prefer to remain anonymous)
- Listed in our security hall of fame
- Eligible for swag (if available)

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GCP Security Best Practices](https://cloud.google.com/security/best-practices)
- [Python Security Guide](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [Terraform Security Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/part1.html)

---

**Last Updated**: October 2025

Thank you for helping keep Bangkok AQI Pipeline secure! 🔒
