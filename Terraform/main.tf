

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.18.1"

    }
  }
}

provider "google" {
  project = "upi-transaction-analytics"
  region  = "asia-south1"
}


resource "google_storage_bucket" "upi_data" {
  name          = "upi-transaction-analytics-upi-data"
  location      = "ASIA-SOUTH1"
  force_destroy = true # For easy cleanup
}

# BigQuery dataset
resource "google_bigquery_dataset" "upi" {
  dataset_id = "upi_analytics"
  location   = "asia-south1"
}
