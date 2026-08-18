"""
extract.py
Reads raw CSV files from data/raw/ and reports what came in.
This is Step 1 of the pipeline: Extract.
"""

import pandas as pd
from datetime import datetime
import os

RAW_DATA_PATH = "data/raw"

FILES_TO_EXTRACT = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "customers": "olist_customers_dataset.csv",
}


def extract_file(name, filename):
    filepath = os.path.join(RAW_DATA_PATH, filename)

    if not os.path.exists(filepath):
        print(f"[ERROR] Could not find {filepath}")
        return None

    df = pd.read_csv(filepath)

    print(f"\n--- {name} ---")
    print(f"File: {filename}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(f"Extracted at: {datetime.now().isoformat()}")

    return df


def main():
    print("Starting extraction...")
    extracted_data = {}

    for name, filename in FILES_TO_EXTRACT.items():
        df = extract_file(name, filename)
        if df is not None:
            extracted_data[name] = df

    print("\nExtraction complete.")
    print(f"Successfully extracted {len(extracted_data)} of {len(FILES_TO_EXTRACT)} files.")

    return extracted_data


if __name__ == "__main__":
    main()
