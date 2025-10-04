output "batch_config_template" {
  description = "Template configuration for Dataproc Serverless batch jobs"
  value = {
    runtime_config = {
      version = "2.1"
      properties = {
        "spark.dynamicAllocation.enabled" = "true"
        "spark.executor.instances"        = "2"
        "spark.driver.memory"             = "2g"
        "spark.executor.memory"           = "2g"
        "spark.executor.cores"            = "2"
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
