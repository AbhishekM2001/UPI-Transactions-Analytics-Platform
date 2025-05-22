import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd


def scrape_rbi_upi_data():
    # Constants
    BASE_URL = "https://www.rbi.org.in/"
    TARGET_URL = "https://www.rbi.org.in/scripts/EntityWiseRetailStatistics.aspx"
    OUTPUT_DIR = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../Dataset/Raw"
    )
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Step 1: Fetch the webpage
    print("Fetching RBI UPI statistics page...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return None

    # Step 2: Parse the page to find Excel links
    soup = BeautifulSoup(response.content, "html.parser")

    # Generate a list of values from April 2024 to April 2030
    date_values = []
    for year in range(2024, 2031):
        for month in range(1, 13):
            if year == 2024 and month < 4:
                continue
            if year == 2030 and month > 4:
                break
            date_values.append(f"{year}-{month:02}")

    # Find all Excel links (looking for typical RBI download links)
    excel_links = []
    for link in soup.find_all("a", href=True):
        href = link["href"].lower()
        if href.endswith((".xls", ".xlsx")):
            full_url = urljoin(BASE_URL, link["href"])
            excel_links.append(["", full_url])

    if not excel_links:
        print("No Excel files found on the page")
        return None

    # Reverse the excel_links list
    excel_links.reverse()
    k = 0
    for link in excel_links:
        monthyear = date_values[k]
        link[0] = monthyear
        k += 1

    # Step 3: Download the file
    for link in excel_links:
        try:
            file_response = requests.get(link[1], headers=headers, timeout=30)
            file_response.raise_for_status()

            # Save with original filename
            filename = os.path.join(OUTPUT_DIR, "upi_dataset_" + link[0] + ".xlsx")
            with open(filename, "wb") as f:
                f.write(file_response.content)
            print(f"Successfully downloaded: {filename}")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading file {link[1]}: {e}")


if __name__ == "__main__":
    excel_file = scrape_rbi_upi_data()
    print("Data scraping and processing completed successfully!")
