# This module sets up IAM permissions and configurations for Dataproc Serverless
# Actual batch jobs will be submitted via Airflow or CLI

# Additional IAM permissions are already handled in the IAM module
# This module can be extended to create reusable batch templates

# Dataproc batch template (optional)
# Can be used to standardize Spark job configurations
locals {
  batch_config_template = {
    runtime_config = {
      version = "2.1"
      properties = {
        "spark.dynamicAllocation.enabled"    = "true"
        "spark.executor.instances"           = "2"
        "spark.driver.memory"                = "2g"
        "spark.executor.memory"              = "2g"
        "spark.executor.cores"               = "2"
      }
    }
    environment_config = {
      execution_config = {
        service_account = var.service_account_email
        subnetwork_uri  = "default"
      }
    }
  }
}

# Output the template for reference
output "batch_config_template" {
  description = "Template configuration for Dataproc Serverless batch jobs"
  value       = local.batch_config_template
}
