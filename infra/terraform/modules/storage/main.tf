# Raw data bucket
resource "google_storage_bucket" "raw" {
  name          = var.gcs_bucket_raw
  location      = var.region
  project       = var.project_id
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90 # days
    }
    action {
      type = "Delete"
    }
  }

  lifecycle_rule {
    condition {
      age                = 30
      matches_prefix     = ["date="]
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  labels = merge(var.labels, {
    purpose = "raw-data-storage"
  })
}

# Quarantine bucket for bad records
resource "google_storage_bucket" "quarantine" {
  name          = var.gcs_bucket_quarantine
  location      = var.region
  project       = var.project_id
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 180 # days - keep bad records longer for debugging
    }
    action {
      type = "Delete"
    }
  }

  labels = merge(var.labels, {
    purpose = "quarantine-data-storage"
  })
}
