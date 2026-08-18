"""
load.py
Loads the transformed data into Postgres.
Also logs the pipeline run (timestamp, row counts, status) into a tracking table.
This is Step 4 of the pipeline: Load.
"""

import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
import os

PROCESSED_PATH = "data/processed"
INPUT_FILE = os.path.join(PROCESSED_PATH, "orders_enriched.csv")

# Connection details match docker-compose.yml
DB_USER = "etl_user"
DB_PASSWORD = "etl_password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "etl_warehouse"

DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def get_engine():
    return create_engine(DB_URL)


def create_run_log_table(engine):
    """Creates the pipeline_run_log table if it doesn't exist yet."""
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS pipeline_run_log (
                id SERIAL PRIMARY KEY,
                run_timestamp TIMESTAMP,
                rows_loaded INTEGER,
                status TEXT
            )
        """))
        conn.commit()


def load_data(engine):
    print(f"Reading {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)
    print(f"  {len(df)} rows found")

    print("Loading into Postgres table 'orders_enriched'...")
    df.to_sql("orders_enriched", engine, if_exists="replace", index=False)
    print(f"  Loaded {len(df)} rows successfully")

    return len(df)


def log_run(engine, rows_loaded, status):
    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO pipeline_run_log (run_timestamp, rows_loaded, status)
                VALUES (:ts, :rows, :status)
            """),
            {"ts": datetime.now(), "rows": rows_loaded, "status": status},
        )
        conn.commit()
    print(f"Logged run: {rows_loaded} rows, status={status}")


def main():
    print("Starting load...")
    engine = get_engine()

    create_run_log_table(engine)

    try:
        rows_loaded = load_data(engine)
        log_run(engine, rows_loaded, "SUCCESS")
        print("\nLoad complete.")
    except Exception as e:
        print(f"[ERROR] Load failed: {e}")
        log_run(engine, 0, "FAILED")


if __name__ == "__main__":
    main()
