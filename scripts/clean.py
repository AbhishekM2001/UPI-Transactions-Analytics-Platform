import pandas as pd
from datetime import datetime
import os
from glob import glob

# Get all .xlsx files in the Dataset/Raw folder
raw_files = glob("./Dataset/Raw/*.xlsx")
print(f"Found {len(raw_files)} raw files to process.")

for file_path in raw_files:
    # Read the Excel file
    df = pd.read_excel(file_path, header=None, skiprows=3)
    if df[0].isnull().all():
        df = df.drop(columns=[0])

    # Manual column naming
    df.columns = [
        "sr_no",
        "entity_name",
        "remitter_volume_lakh",
        "remitter_value_cr",
        "beneficiary_volume_lakh",
        "beneficiary_value_cr",
    ]

    # Remove rows with NULL entity names
    df = df[df["entity_name"].notna()]

    # Extract the month-year from the filename
    filename = os.path.basename(file_path)
    monthyear = filename[-12:-5]  # Assuming the format is consistent

    # Convert the month-year string to a datetime object
    month = datetime.strptime(monthyear, "%Y-%m").strftime("%Y-%m")
    # Add a new column with the month-year
    df["month"] = month

    # Convert the 'sr_no' column to numeric, forcing errors to NaN
    df["sr_no"] = pd.to_numeric(df["sr_no"], errors="coerce")
    # Drop rows where 'sr_no' is NaN
    df = df.dropna(subset=["sr_no"])
    # Convert 'sr_no' back to integer
    df["sr_no"] = df["sr_no"].astype(int)

    # Remove rows where 'entity_name' is "Total"
    df = df[df["entity_name"] != "Total"]

    # Save cleaned CSV
    cleaned_file_path = f"./Dataset/Cleaned/upi_dataset_{monthyear}.csv"
    df.to_csv(cleaned_file_path, index=False)
