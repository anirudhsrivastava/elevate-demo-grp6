from google.cloud import bigquery
import os

GCP_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "geap-poc")
client = bigquery.Client(project=GCP_PROJECT)
dataset_id = f"{GCP_PROJECT}.hr_policies_dataset"
table_id = f"{dataset_id}.hr_policies"

try:
    table = client.get_table(table_id)
    print(f"Table {table_id} exists.")
except Exception as e:
    print(f"Table not found or error: {e}")
