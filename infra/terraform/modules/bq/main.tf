# Staging dataset
resource "google_bigquery_dataset" "staging" {
  dataset_id    = var.dataset_staging
  project       = var.project_id
  location      = var.location
  friendly_name = "AQI Staging Dataset"
  description   = "Staging tables for raw weather and air quality data"

  default_table_expiration_ms = 7776000000 # 90 days

  default_partition_expiration_ms = 7776000000 # 90 days for partitioned tables

  labels = merge(var.labels, {
    layer = "staging"
  })
}

# Marts dataset
resource "google_bigquery_dataset" "marts" {
  dataset_id    = var.dataset_marts
  project       = var.project_id
  location      = var.location
  friendly_name = "AQI Marts Dataset"
  description   = "Analytics-ready mart tables for AQI and weather"

  # No expiration for marts - production data
  
  labels = merge(var.labels, {
    layer = "marts"
  })
}

# Example staging table schemas (can be managed by Spark/dbt instead)
resource "google_bigquery_table" "weather_hourly" {
  dataset_id          = google_bigquery_dataset.staging.dataset_id
  project             = var.project_id
  table_id            = "weather_hourly"
  deletion_protection = false

  time_partitioning {
    type  = "HOUR"
    field = "event_hour"
  }

  clustering = ["source"]

  schema = jsonencode([
    {
      name        = "event_hour"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "Event timestamp (hourly grain)"
    },
    {
      name        = "latitude"
      type        = "FLOAT64"
      mode        = "NULLABLE"
    },
    {
      name        = "longitude"
      type        = "FLOAT64"
      mode        = "NULLABLE"
    },
    {
      name        = "temperature_2m"
      type        = "FLOAT64"
      mode        = "NULLABLE"
      description = "Temperature at 2m in Celsius"
    },
    {
      name        = "relative_humidity_2m"
      type        = "FLOAT64"
      mode        = "NULLABLE"
    },
    {
      name        = "precipitation"
      type        = "FLOAT64"
      mode        = "NULLABLE"
    },
    {
      name        = "wind_speed_10m"
      type        = "FLOAT64"
      mode        = "NULLABLE"
    },
    {
      name        = "wind_direction_10m"
      type        = "FLOAT64"
      mode        = "NULLABLE"
    },
    {
      name        = "source"
      type        = "STRING"
      mode        = "NULLABLE"
    },
    {
      name        = "ingested_at"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
    }
  ])

  labels = var.labels
}

resource "google_bigquery_table" "aqi_hourly" {
  dataset_id          = google_bigquery_dataset.staging.dataset_id
  project             = var.project_id
  table_id            = "aqi_hourly"
  deletion_protection = false

  time_partitioning {
    type  = "HOUR"
    field = "event_hour"
  }

  clustering = ["source"]

  schema = jsonencode([
    {
      name        = "event_hour"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "Event timestamp (hourly grain)"
    },
    {
      name        = "latitude"
      type        = "FLOAT64"
      mode        = "NULLABLE"
    },
    {
      name        = "longitude"
      type        = "FLOAT64"
      mode        = "NULLABLE"
    },
    {
      name        = "pm10"
      type        = "FLOAT64"
      mode        = "NULLABLE"
    },
    {
      name        = "pm2_5"
      type        = "FLOAT64"
      mode        = "NULLABLE"
    },
    {
      name        = "carbon_monoxide"
      type        = "FLOAT64"
      mode        = "NULLABLE"
    },
    {
      name        = "nitrogen_dioxide"
      type        = "FLOAT64"
      mode        = "NULLABLE"
    },
    {
      name        = "sulphur_dioxide"
      type        = "FLOAT64"
      mode        = "NULLABLE"
    },
    {
      name        = "ozone"
      type        = "FLOAT64"
      mode        = "NULLABLE"
    },
    {
      name        = "us_aqi"
      type        = "INT64"
      mode        = "NULLABLE"
      description = "US EPA AQI"
    },
    {
      name        = "european_aqi"
      type        = "INT64"
      mode        = "NULLABLE"
      description = "European AQI"
    },
    {
      name        = "source"
      type        = "STRING"
      mode        = "NULLABLE"
    },
    {
      name        = "ingested_at"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
    }
  ])

  labels = var.labels
}
