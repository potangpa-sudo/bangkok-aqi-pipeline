resource "google_composer_environment" "composer_env" {
  name    = var.environment_name
  region  = var.region
  project = var.project_id

  labels = var.labels

  config {
    software_config {
      image_version = "composer-2-airflow-2"
      
      pypi_packages = {
        "apache-airflow-providers-google" = ">=10.0.0"
        "pandas"                          = ">=2.0.0"
        "requests"                        = ">=2.31.0"
      }

      airflow_config_overrides = var.airflow_config_overrides

      env_variables = merge(var.env_variables, {
        AIRFLOW__CORE__DEFAULT_TIMEZONE = "Asia/Bangkok"
      })
    }

    workloads_config {
      scheduler {
        cpu        = 0.5
        memory_gb  = 2
        storage_gb = 1
        count      = 1
      }

      web_server {
        cpu        = 0.5
        memory_gb  = 2
        storage_gb = 1
      }

      worker {
        cpu        = 0.5
        memory_gb  = 2
        storage_gb = 1
        min_count  = 1
        max_count  = 3
      }
    }

    environment_size = "ENVIRONMENT_SIZE_SMALL"

    node_config {
      service_account = var.service_account_email
    }
  }

  timeouts {
    create = "60m"
    update = "60m"
    delete = "60m"
  }
}
