# Bangkok AQI Pipeline - PR Checklist

Use this template when opening pull requests for the pipeline.

## PR Type
- [ ] Feature
- [ ] Bug fix
- [ ] Refactor
- [ ] Documentation
- [ ] Infrastructure change

## Description

_Describe what this PR does and why._

## Changes

- [ ] Added/modified files in `src/`
- [ ] Added/modified files in `infra/terraform/`
- [ ] Added/modified files in `airflow/dags/`
- [ ] Added/modified files in `spark/`
- [ ] Added/modified files in `dbt/models/`
- [ ] Updated documentation
- [ ] Updated tests

## Testing

- [ ] Tested locally
- [ ] Unit tests pass
- [ ] Integration tests pass (if applicable)
- [ ] Terraform plan succeeds
- [ ] dbt compile succeeds
- [ ] CI pipeline passes

## Deployment

- [ ] Changes are backward compatible
- [ ] No breaking schema changes
- [ ] Deployment plan documented
- [ ] Rollback plan documented

## Checklist

- [ ] Code follows project style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No hardcoded secrets
- [ ] Commit messages are clear
- [ ] PR description is complete

## Screenshots (if applicable)

_Add screenshots of dashboard changes, Airflow DAG, etc._

## Related Issues

Closes #_issue_number_

## Deployment Notes

_Add any special instructions for deploying this PR._

## Rollback Plan

_Describe how to rollback if deployment fails._
