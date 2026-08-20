from google.cloud import bigquery
import os
import datetime

GCP_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "geap-poc")
client = bigquery.Client(project=GCP_PROJECT)
dataset_id = f"{GCP_PROJECT}.hr_policies_dataset"
table_id = f"{dataset_id}.hr_policies"

# Read the extracted text
with open("/usr/local/google/home/anujshaunj/hr-agentic-solution/hr-agentic-solution/handbook.txt", "r") as f:
    handbook_content = f.read()

# Create a row to insert
rows_to_insert = [
    {
        "doc_id": "ALT-HB-2026",
        "title": "Altostrat Singapore Employee Policy Handbook",
        "category": "General HR Policies",
        "content": handbook_content,
        "source_url": "https://github.com/tanyagoogle/elevate-hr-policy-agent/blob/main/data/handbook.pdf",
        "tags": "handbook, policies, singapore, altostrat, bereavement, leave",
        "last_updated": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
]

# Insert the row
errors = client.insert_rows_json(table_id, rows_to_insert)
if errors == []:
    print("New rows have been added.")
else:
    print("Encountered errors while inserting rows: {}".format(errors))
