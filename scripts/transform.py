"""
transform.py
Cleans, merges, and enriches the validated data.
Joins orders + order_items + customers, computes derived fields.
This is Step 3 of the pipeline: Transform.
"""

import pandas as pd
import os

RAW_DATA_PATH = "data/raw"
PROCESSED_PATH = "data/processed"

os.makedirs(PROCESSED_PATH, exist_ok=True)


def load_clean_data():
    """In a full pipeline this would take validate.py's output directly.
    For now we re-read raw files since Olist has no rejected rows to exclude."""
    orders = pd.read_csv(os.path.join(RAW_DATA_PATH, "olist_orders_dataset.csv"))
    order_items = pd.read_csv(os.path.join(RAW_DATA_PATH, "olist_order_items_dataset.csv"))
    customers = pd.read_csv(os.path.join(RAW_DATA_PATH, "olist_customers_dataset.csv"))
    return orders, order_items, customers


def clean_types(orders, order_items):
    """Convert date columns to proper datetime type."""
    date_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for col in date_cols:
        orders[col] = pd.to_datetime(orders[col], errors="coerce")

    order_items["shipping_limit_date"] = pd.to_datetime(
        order_items["shipping_limit_date"], errors="coerce"
    )

    return orders, order_items


def deduplicate(orders, order_items, customers):
    before = (len(orders), len(order_items), len(customers))
    orders = orders.drop_duplicates(subset="order_id")
    order_items = order_items.drop_duplicates()
    customers = customers.drop_duplicates(subset="customer_id")
    after = (len(orders), len(order_items), len(customers))

    print(f"  Orders: {before[0]} -> {after[0]}")
    print(f"  Order items: {before[1]} -> {after[1]}")
    print(f"  Customers: {before[2]} -> {after[2]}")

    return orders, order_items, customers


def compute_order_value(order_items):
    """Total order value per order_id = sum of price + freight across items."""
    order_value = order_items.groupby("order_id").agg(
        total_price=("price", "sum"),
        total_freight=("freight_value", "sum"),
        item_count=("order_item_id", "count"),
    ).reset_index()

    order_value["total_order_value"] = order_value["total_price"] + order_value["total_freight"]
    return order_value


def compute_delivery_delay(orders):
    """Delivery delay in days: actual delivery date vs estimated delivery date.
    Positive = delivered late, negative = delivered early."""
    orders["delivery_delay_days"] = (
        orders["order_delivered_customer_date"] - orders["order_estimated_delivery_date"]
    ).dt.days
    return orders


def merge_all(orders, order_value, customers):
    merged = orders.merge(order_value, on="order_id", how="left")
    merged = merged.merge(customers, on="customer_id", how="left")
    return merged


def main():
    print("Starting transformation...")

    orders, order_items, customers = load_clean_data()

    print("\n--- Cleaning types ---")
    orders, order_items = clean_types(orders, order_items)

    print("\n--- Deduplicating ---")
    orders, order_items, customers = deduplicate(orders, order_items, customers)

    print("\n--- Computing derived fields ---")
    order_value = compute_order_value(order_items)
    orders = compute_delivery_delay(orders)

    print("\n--- Merging into final dataset ---")
    final_df = merge_all(orders, order_value, customers)
    print(f"  Final dataset shape: {final_df.shape[0]} rows, {final_df.shape[1]} columns")

    output_path = os.path.join(PROCESSED_PATH, "orders_enriched.csv")
    final_df.to_csv(output_path, index=False)
    print(f"\nSaved cleaned dataset to {output_path}")

    print("\nTransformation complete.")
    return final_df


if __name__ == "__main__":
    main()
