from google.cloud import storage
from google.oauth2 import service_account

# Path to your service account key
SERVICE_ACCOUNT_KEY = "./Terraform/Terraform_keys.json"

# Initialize client
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY)
storage_client = storage.Client(credentials=credentials)


def upload_to_gcs(bucket_name, source_file, destination_blob_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file)
    print(f"File uploaded to gs://{bucket_name}/{destination_blob_name}")


# Replace these values
upload_to_gcs(
    bucket_name="upi-transaction-analytics-upi-data",  # From Terraform output
    source_file="./Dataset/Cleaned/cleaned_upi_dataset_2025-01.csv",
    destination_blob_name="cleaned/upi_data_2025-01.csv",
)
