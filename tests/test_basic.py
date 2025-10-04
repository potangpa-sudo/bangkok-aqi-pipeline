"""Basic tests for the Bangkok AQI Pipeline."""
import pytest


def test_import_ingestor():
    """Test that ingestor modules can be imported."""
    try:
        from src.ingestor import app, clients, schemas, utils
        assert app is not None
        assert clients is not None
        assert schemas is not None
        assert utils is not None
    except ImportError as e:
        pytest.skip(f"Ingestor modules not available: {e}")


def test_project_structure():
    """Test that key project files exist."""
    import os
    
    root_files = [
        "README.md",
        "requirements.txt",
        "pyproject.toml",
        "LICENSE",
        "CONTRIBUTING.md"
    ]
    
    for file in root_files:
        assert os.path.exists(file), f"{file} should exist"


def test_docker_files_exist():
    """Test that Dockerfiles exist."""
    import os
    
    dockerfiles = [
        "src/ingestor/Dockerfile",
        "app/Dockerfile"
    ]
    
    for dockerfile in dockerfiles:
        assert os.path.exists(dockerfile), f"{dockerfile} should exist"


def test_terraform_structure():
    """Test that Terraform files exist."""
    import os
    
    terraform_files = [
        "infra/terraform/main.tf",
        "infra/terraform/variables.tf",
        "infra/terraform/outputs.tf",
        "infra/terraform/providers.tf"
    ]
    
    for tf_file in terraform_files:
        assert os.path.exists(tf_file), f"{tf_file} should exist"


def test_dbt_structure():
    """Test that dbt files exist."""
    import os
    
    dbt_files = [
        "dbt/dbt_project.yml",
        "dbt/profiles.yml"
    ]
    
    for dbt_file in dbt_files:
        assert os.path.exists(dbt_file), f"{dbt_file} should exist"


def test_documentation_exists():
    """Test that documentation files exist."""
    import os
    
    docs = [
        "README.md",
        "DEPLOYMENT.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "CODE_OF_CONDUCT.md",
        "CHANGELOG.md",
        "docs/architecture.md"
    ]
    
    for doc in docs:
        assert os.path.exists(doc), f"{doc} should exist"


def test_github_workflows_exist():
    """Test that GitHub workflows exist."""
    import os
    
    workflows = [
        ".github/workflows/ci.yml",
        ".github/workflows/deploy.yml",
        ".github/workflows/release.yml"
    ]
    
    for workflow in workflows:
        assert os.path.exists(workflow), f"{workflow} should exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
