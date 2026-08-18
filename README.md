# ETL Pipeline with Data Quality Monitoring

An end-to-end data engineering pipeline that ingests raw e-commerce data, runs automated data quality checks, transforms and enriches it, loads it into a Postgres warehouse, and visualizes pipeline health and business insights on a live dashboard.

Built to demonstrate Data Engineer, Data Analyst, and Software Engineer skills in one project: orchestration-ready pipeline design, SQL warehousing, data validation, and dashboarding.

## Architecture

Raw CSVs (data/raw/)
      |
      v
  extract.py   -> reads and reports on raw files
      |
      v
  validate.py  -> checks for nulls, duplicates, bad dates, referential integrity
      |          -> failing rows saved to data/rejected/
      v
  transform.py -> cleans types, deduplicates, joins tables, computes derived fields
      |          -> (total order value, delivery delay)
      v
  load.py      -> loads clean data into Postgres, logs each pipeline run
      |
      v
  Postgres (Docker) -> orders_enriched, pipeline_run_log tables
      |
      v
  dashboard.py -> Streamlit dashboard, live queries against Postgres

## Dataset

[Olist Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) - real anonymized order data from a Brazilian e-commerce marketplace, including orders, order items, and customers across ~99,000 orders.

## Tech Stack

- Language: Python (pandas, SQLAlchemy)
- Warehouse: PostgreSQL, running in Docker
- Dashboard: Streamlit
- Containerization: Docker + docker-compose
- Orchestration: Apache Airflow (DAG included, see dags/)
- Version control: Git/GitHub

## What the pipeline checks

- No missing order_id / customer_id
- No duplicate order_ids
- Valid, parseable order timestamps
- No negative prices or freight values
- Referential integrity: every order_id in order_items must exist in orders

Failing rows are never silently dropped - they are written to data/rejected/ with a clear reason, and every pipeline run is logged (timestamp, rows loaded, status) into a pipeline_run_log table in Postgres.

## Derived metrics computed

- Total order value - sum of item price + freight per order
- Delivery delay (days) - actual delivery date vs. estimated delivery date (positive = late, negative = early)

## How to run this locally

### 1. Prerequisites
- Python 3.10+
- Docker Desktop
- Git

### 2. Clone and set up

git clone https://github.com/sdiveshh/etl-data-quality-pipeline.git
cd etl-data-quality-pipeline
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

### 3. Download the dataset

Download the Olist dataset from Kaggle and place the CSVs in data/raw/.

### 4. Start Postgres

docker-compose up -d

### 5. Run the pipeline

python scripts/extract.py
python scripts/validate.py
python scripts/transform.py
python scripts/load.py

### 6. Launch the dashboard

streamlit run dashboard.py

Visit http://localhost:8501 to view pipeline health, data quality summary, and business insights.

## Project Structure

etl-data-quality-pipeline/
|-- dags/                  # Airflow DAG definitions
|-- data/
|   |-- raw/                # Raw input CSVs (gitignored)
|   |-- processed/          # Cleaned output (gitignored)
|   |-- rejected/           # Rows that failed validation (gitignored)
|-- scripts/
|   |-- extract.py
|   |-- validate.py
|   |-- transform.py
|   |-- load.py
|-- dashboard.py            # Streamlit dashboard
|-- docker-compose.yml      # Postgres service
|-- requirements.txt
|-- README.md

## What I'd do differently at scale

- Swap static file ingestion for streaming ingestion (Kafka + a producer script)
- Use Great Expectations instead of custom validation checks for a more standardized DQ framework
- Deploy Postgres and Airflow to AWS (RDS + EC2) instead of running locally
- Add automated tests for each pipeline stage

## Author

Divesh Singh
[GitHub](https://github.com/sdiveshh)
