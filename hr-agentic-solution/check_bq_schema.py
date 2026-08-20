from google.cloud import bigquery
import os

GCP_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "geap-poc")
client = bigquery.Client(project=GCP_PROJECT)
dataset_id = f"{GCP_PROJECT}.hr_policies_dataset"
table_id = f"{dataset_id}.hr_policies"

table = client.get_table(table_id)
for schema_field in table.schema:
    print(f"{schema_field.name}: {schema_field.field_type}")
