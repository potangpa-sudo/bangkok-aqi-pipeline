# Contributing to Bangkok AQI Pipeline

Thank you for your interest in contributing to the Bangkok AQI Pipeline! This document provides guidelines and instructions for contributing.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)
- [Component-Specific Guidelines](#component-specific-guidelines)

## Code of Conduct

### Our Pledge
We are committed to providing a welcoming and inclusive environment for all contributors.

### Standards
- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites
- Python 3.11+
- Terraform 1.5.0+
- Docker Desktop
- GCP account with billing enabled
- Git

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/bangkok-aqi-pipeline.git
   cd bangkok-aqi-pipeline
   ```

2. **Install Development Dependencies**
   ```bash
   # Install pre-commit hooks
   pip install pre-commit
   pre-commit install
   
   # Install Python dependencies
   pip install -r requirements.txt
   pip install -r src/ingestor/requirements.txt
   pip install -r dbt/requirements.txt
   
   # Install development tools
   pip install ruff mypy pytest pytest-cov
   ```

3. **Set Up Local Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your local values
   ```

4. **Verify Installation**
   ```bash
   # Run linting
   ruff check .
   
   # Run type checking
   mypy src/
   
   # Run tests
   pytest
   ```

## Development Workflow

### Branch Naming Convention
- `feature/` - New features (e.g., `feature/add-retry-logic`)
- `fix/` - Bug fixes (e.g., `fix/partition-date-handling`)
- `docs/` - Documentation updates (e.g., `docs/improve-readme`)
- `refactor/` - Code refactoring (e.g., `refactor/spark-job-structure`)
- `test/` - Test additions/improvements (e.g., `test/add-integration-tests`)
- `chore/` - Maintenance tasks (e.g., `chore/update-dependencies`)

### Workflow Steps

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write clean, documented code
   - Follow coding standards (see below)
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Locally**
   ```bash
   # Run linting
   ruff check .
   
   # Run type checking
   mypy src/
   
   # Run tests
   pytest --cov
   
   # Test specific component
   cd src/ingestor && pytest
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add retry logic to ingestor"
   ```
   
   Use conventional commit messages:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Code style changes (formatting)
   - `refactor:` - Code refactoring
   - `test:` - Adding or updating tests
   - `chore:` - Maintenance tasks

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line Length**: 100 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings
- **Imports**: Sorted alphabetically, grouped by standard library, third-party, local

### Code Formatting

We use **Ruff** for linting and formatting:

```bash
# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

### Type Hints

All functions should have type hints:

```python
def process_data(raw_data: dict[str, Any], partition_date: str) -> pd.DataFrame:
    """Process raw data into a DataFrame.
    
    Args:
        raw_data: Dictionary containing raw API response
        partition_date: Date string in YYYY-MM-DD format
        
    Returns:
        Processed DataFrame with standardized columns
        
    Raises:
        ValueError: If raw_data is missing required fields
    """
    ...
```

### Documentation

- **Docstrings**: Use Google-style docstrings for all public functions/classes
- **Comments**: Explain "why", not "what" (code should be self-documenting)
- **READMEs**: Update component READMEs when changing functionality

### Error Handling

```python
# Good - Specific exceptions with context
try:
    data = fetch_api_data(url)
except requests.HTTPError as e:
    logger.error(f"Failed to fetch data from {url}: {e}")
    raise DataIngestionError(f"API request failed: {e}") from e

# Bad - Bare except
try:
    data = fetch_api_data(url)
except:
    pass
```

## Testing Guidelines

### Test Structure

```
tests/
├── unit/           # Unit tests (fast, isolated)
├── integration/    # Integration tests (slower, external deps)
└── e2e/           # End-to-end tests (full pipeline)
```

### Writing Tests

```python
import pytest
from src.ingestor.clients import GCSClient

class TestGCSClient:
    @pytest.fixture
    def gcs_client(self):
        return GCSClient(bucket_name="test-bucket")
    
    def test_write_json_success(self, gcs_client, mocker):
        """Test successful JSON write to GCS."""
        mock_blob = mocker.patch.object(gcs_client.bucket, 'blob')
        
        gcs_client.write_json({"key": "value"}, "test.json")
        
        mock_blob.assert_called_once_with("test.json")
        mock_blob.return_value.upload_from_string.assert_called_once()
    
    def test_write_json_failure(self, gcs_client, mocker):
        """Test GCS write failure handling."""
        mocker.patch.object(
            gcs_client.bucket, 
            'blob', 
            side_effect=Exception("GCS error")
        )
        
        with pytest.raises(Exception, match="GCS error"):
            gcs_client.write_json({"key": "value"}, "test.json")
```

### Test Coverage

- Aim for **80%+ code coverage**
- All public functions must have tests
- Critical paths must have integration tests

```bash
# Run with coverage
pytest --cov=src --cov-report=html

# View report
open htmlcov/index.html
```

## Submitting Changes

### Before Submitting

- [ ] Code passes all linting checks (`ruff check .`)
- [ ] Type checking passes (`mypy src/`)
- [ ] All tests pass (`pytest`)
- [ ] Test coverage is adequate
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] Branch is up to date with main

### Pull Request Process

1. **Fill Out PR Template**
   - Provide clear description of changes
   - Link related issues
   - Add screenshots if UI changes
   - Complete checklist

2. **Wait for CI Checks**
   - All GitHub Actions must pass
   - Fix any failing checks

3. **Address Review Comments**
   - Respond to all comments
   - Make requested changes
   - Mark conversations as resolved

4. **Merge Requirements**
   - At least 1 approving review
   - All CI checks passing
   - No merge conflicts
   - Up to date with main branch

### After Merge

- Delete your feature branch
- Close related issues
- Update project board if applicable

## Component-Specific Guidelines

### Terraform (Infrastructure)

- **Modules**: Create reusable modules for common patterns
- **Variables**: Always provide descriptions and validation
- **Outputs**: Export all useful values
- **Formatting**: Run `terraform fmt -recursive`
- **Validation**: Run `terraform validate` before committing

```hcl
variable "environment" {
  type        = string
  description = "Deployment environment (dev, staging, prod)"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod"
  }
}
```

### FastAPI (Ingestor)

- **Endpoints**: Use appropriate HTTP methods and status codes
- **Validation**: Use Pydantic models for request/response
- **Error Handling**: Return structured error responses
- **Documentation**: Add docstrings for OpenAPI docs
- **Logging**: Log at appropriate levels (INFO, WARNING, ERROR)

```python
@app.post("/ingest/hourly", status_code=status.HTTP_201_CREATED)
async def ingest_hourly(
    city: str = Query(..., description="City name for weather data"),
    hour_offset: int = Query(0, ge=-24, le=0, description="Hour offset from current time")
) -> IngestionResponse:
    """Ingest hourly weather and AQI data for a city.
    
    This endpoint fetches data from Open-Meteo API and stores it in GCS.
    """
    ...
```

### PySpark (Data Processing)

- **Performance**: Minimize shuffles, use broadcast joins when appropriate
- **Partitioning**: Always partition large datasets
- **Error Handling**: Use try-except within UDFs
- **Logging**: Use logger instead of print statements
- **Testing**: Test transformations with small sample data

```python
# Good - Efficient join with broadcast
from pyspark.sql import functions as F

small_df_broadcast = F.broadcast(small_df)
result = large_df.join(small_df_broadcast, "key")

# Good - Proper error handling in UDF
@F.udf(returnType=StringType())
def safe_transform(value):
    try:
        return transform_logic(value)
    except Exception as e:
        logger.warning(f"Transform failed: {e}")
        return None
```

### dbt (Data Transformations)

- **Naming**: Use consistent prefixes (stg_, fact_, mart_)
- **Documentation**: Document all models in schema.yml
- **Tests**: Add tests for all models
- **Materialization**: Use appropriate materialization strategy
- **Macros**: Create reusable macros for common logic

```sql
-- models/staging/stg_weather.sql
{{ config(
    materialized='view',
    tags=['staging', 'weather']
) }}

with source as (
    select * from {{ source('raw', 'weather_hourly') }}
),

transformed as (
    select
        event_hour,
        temperature_2m,
        -- Add business logic here
    from source
)

select * from transformed
```

### Airflow (Orchestration)

- **DAG Structure**: Keep DAGs simple and readable
- **Dependencies**: Define explicit task dependencies
- **Retries**: Configure appropriate retry logic
- **SLAs**: Set realistic SLAs
- **Variables**: Use Airflow Variables for configuration

```python
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email_on_retry': False,
}

with DAG(
    'aqi_hourly_pipeline',
    default_args=default_args,
    description='Hourly AQI data pipeline',
    schedule_interval='0 * * * *',
    start_date=datetime(2024, 1, 1, tzinfo=timezone(timedelta(hours=7))),
    catchup=False,
    tags=['production', 'aqi'],
) as dag:
    ...
```

### Streamlit (Dashboard)

- **Performance**: Use `@st.cache_data` for expensive operations
- **Layout**: Use columns and containers for organization
- **Interactivity**: Add filters and controls
- **Error Handling**: Show user-friendly error messages
- **Responsiveness**: Test on different screen sizes

```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data(start_date: str, end_date: str) -> pd.DataFrame:
    """Load and cache dashboard data."""
    ...

# Good - User-friendly error handling
try:
    data = load_data(start_date, end_date)
    st.dataframe(data)
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.info("Please try refreshing or contact support.")
```

## Questions or Issues?

- 📧 **Email**: Create an issue on GitHub
- 💬 **Discussions**: Use GitHub Discussions for questions
- 🐛 **Bugs**: Create a bug report using the template
- ✨ **Features**: Create a feature request using the template

## Recognition

Contributors will be recognized in:
- The README.md contributors section
- Release notes for significant contributions
- The project's GitHub insights

Thank you for contributing to the Bangkok AQI Pipeline! 🎉
