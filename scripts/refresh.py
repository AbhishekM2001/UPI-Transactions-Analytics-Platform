from google.cloud import bigquery
from google.cloud import storage
from google.oauth2 import service_account
import os

# Dynamically get the path to the service account key in the config folder
SERVICE_ACCOUNT_KEY = os.path.join(
    os.path.dirname(__file__), "../config/gcp-credentials.json"
)

# Initialize client
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY)
storage_client = storage.Client(credentials=credentials)

client = bigquery.Client(credentials=credentials)
storage_client = storage.Client(credentials=credentials)


def load_new_data():
    """Load new CSV files from GCS to raw table"""
    query = """
    -- Load data from GCS (adjust path and schema as needed)
    LOAD DATA OVERWRITE `upi_analytics.cleaned_data`
    FROM FILES (
    format = 'CSV',
    uris = ['gs://upi-transaction-analytics-upi-data/cleaned/upi_dataset_*.csv'],
    skip_leading_rows = 1
    );
    """
    client.query(query).result()
    print("Step 1: New data loaded to staging")


def refresh_optimized_table():
    """Rebuild optimized table from raw data"""
    query = """
    -- Step 3: Recreate optimized table (auto-overwrites)
CREATE OR REPLACE TABLE `upi_analytics.transactions_optimized`
PARTITION BY transaction_date
CLUSTER BY entity_name, transaction_type
AS (
  SELECT
    DATE(CONCAT(month, '-01')) AS transaction_date,  -- Directly parse YYYY-MM
    entity_name,
    'REMITTER' AS transaction_type,
    remitter_volume_lakh AS volume_lakh,
    remitter_value_cr AS value_cr
  FROM `upi_analytics.cleaned_data`

  UNION ALL

  SELECT
    DATE(CONCAT(month, '-01')) AS transaction_date,  -- Same parsing for beneficiary data
    entity_name,
    'BENEFICIARY' AS transaction_type,
    beneficiary_volume_lakh AS volume_lakh,
    beneficiary_value_cr AS value_cr
  FROM `upi_analytics.cleaned_data`
);    
"""
    client.query(query).result()
    print("Step 2: Optimized table refreshed")


def refresh_views():
    """Recreate all dependent views"""
    queries = [
        # Top Banks View
        """
CREATE OR REPLACE VIEW `upi_analytics.top_banks_view` AS
SELECT
  entity_name as BankName,
  concat(extract(year from transaction_date),lpad(cast(extract(month from transaction_date) as string),2,'0')) as MonthYear,
  ROUND(SUM(value_cr), 2) AS TotalValue_cr,
  ROUND(SUM(volume_lakh)*100000, 0) AS TotalTransactions_cr
FROM `upi_analytics.transactions_optimized`
GROUP BY 1,2
ORDER BY 3 DESC;
        """,
        # Monthly Trend View
        """
CREATE OR REPLACE VIEW `upi_analytics.monthly_trend_view` AS
SELECT
  entity_name as BankName,
  transaction_date as TransactionDate,
  ROUND(SUM(value_cr), 2) AS TotalValue_cr,
  ROUND(SUM(volume_lakh), 2) AS TotalVolume_lakh
FROM `upi_analytics.transactions_optimized`
GROUP BY 1,2
ORDER BY 2;
        """,
    ]

    for q in queries:
        client.query(q).result()
    print("Step 3: Views refreshed")


# def archive_processed_files():
#     """Move processed files to archive folder"""
#     bucket = storage_client.bucket("your-bucket")
#     for blob in bucket.list_blobs(prefix="raw/upi_data_"):
#         new_name = blob.name.replace("raw/", "archive/")
#         bucket.rename_blob(blob, new_name)
#     print("✅ Step 4: Files archived")

if __name__ == "__main__":
    load_new_data()
    refresh_optimized_table()
    refresh_views()
    # archive_processed_files()
    print("Pipeline completed successfully")
