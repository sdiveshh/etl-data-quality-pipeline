"""
dashboard.py
Streamlit dashboard showing pipeline health and business insights.
Connects live to the Postgres warehouse.
"""

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

DB_USER = "etl_user"
DB_PASSWORD = "etl_password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "etl_warehouse"

DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

st.set_page_config(page_title="ETL Pipeline Dashboard", layout="wide")


@st.cache_resource
def get_engine():
    return create_engine(DB_URL)


@st.cache_data(ttl=60)
def load_orders():
    engine = get_engine()
    return pd.read_sql("SELECT * FROM orders_enriched", engine)


@st.cache_data(ttl=60)
def load_run_log():
    engine = get_engine()
    return pd.read_sql("SELECT * FROM pipeline_run_log ORDER BY run_timestamp DESC", engine)


st.title("ETL Pipeline & Data Quality Dashboard")
st.caption("Live view of pipeline health and business insights from the Olist e-commerce dataset")

orders = load_orders()
run_log = load_run_log()

# --- Panel 1: Pipeline Health ---
st.header("Pipeline Health")

col1, col2, col3 = st.columns(3)

latest_run = run_log.iloc[0] if len(run_log) > 0 else None

with col1:
    st.metric("Last Run Status", latest_run["status"] if latest_run is not None else "No runs yet")

with col2:
    st.metric("Rows Loaded (Last Run)", f"{latest_run['rows_loaded']:,}" if latest_run is not None else "-")

with col3:
    st.metric("Total Runs Logged", len(run_log))

st.subheader("Run History")
st.dataframe(run_log, use_container_width=True)

st.divider()

# --- Panel 2: Data Quality ---
st.header("Data Quality Summary")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Orders", f"{len(orders):,}")
with col2:
    missing_delivery = orders["order_delivered_customer_date"].isna().sum()
    st.metric("Orders Not Yet Delivered", f"{missing_delivery:,}")
with col3:
    avg_delay = orders["delivery_delay_days"].mean()
    st.metric("Avg Delivery Delay (days)", f"{avg_delay:.1f}" if pd.notna(avg_delay) else "-")

st.divider()

# --- Panel 3: Business Insights ---
st.header("Business Insights")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Orders by State")
    state_counts = orders["customer_state"].value_counts().head(10)
    st.bar_chart(state_counts)

with col2:
    st.subheader("Delivery Delay Distribution (days)")
    delay_data = orders["delivery_delay_days"].dropna()
    st.bar_chart(delay_data.value_counts().sort_index().head(30))

st.subheader("Total Order Value Distribution")
st.bar_chart(orders["total_order_value"].dropna().round(0).value_counts().sort_index().head(50))

st.caption("Dashboard connects live to Postgres — refresh the page to see the latest pipeline run.")
