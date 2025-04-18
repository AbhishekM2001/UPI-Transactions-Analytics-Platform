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


def upload_to_gcs(bucket_name, source_file, destination_blob_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file)
    print(f"File uploaded to gs://{bucket_name}/{destination_blob_name}")


# Iterate through all .xlsx files in the Dataset/Cleaned folder
cleaned_folder = "./Dataset/Cleaned"
bucket_name = "upi-transaction-analytics-upi-data"  # From Terraform output

for file_name in os.listdir(cleaned_folder):
    if file_name.endswith(".csv"):
        source_file = os.path.join(cleaned_folder, file_name)
        destination_blob_name = f"cleaned/{file_name}"
        upload_to_gcs(
            bucket_name=bucket_name,
            source_file=source_file,
            destination_blob_name=destination_blob_name,
        )
