# Vertex AI Offline Feature Store Demo
Instruction:
Step 1: Install locally
python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

Verify:

python -c "import pyspark; print(pyspark.__version__)"
Step 2: Enable GCP Services
gcloud services enable \
    aiplatform.googleapis.com \
    dataproc.googleapis.com \
    bigquery.googleapis.com \
    storage.googleapis.com \
    cloudbuild.googleapis.com

Verify:

gcloud services list --enabled | grep dataproc
Step 3: Create bucket structure
gsutil mb -l us-central1 gs://vertex-demo
echo test > /tmp/test.txt

gsutil cp /tmp/test.txt gs://vertex-demo/raw/

gsutil cp /tmp/test.txt gs://vertex-demo/templates/

gsutil cp /tmp/test.txt gs://vertex-demo/features/

gsutil cp /tmp/test.txt gs://vertex-demo/spark/

gsutil cp /tmp/test.txt gs://vertex-demo/pipeline-root/
Step 4: Upload Spark job
gsutil cp \
components/spark/feature_generation.py \
gs://vertex-demo/spark/

Verify:

gsutil ls gs://vertex-demo/spark/

Expected:

gs://vertex-demo/spark/feature_generation.py
Step 5: Create sample parquet

Create:

import pandas as pd

df = pd.DataFrame({
    "event_date": [
        "2026-05-01",
        "2026-05-01"
    ],
    "publisher_id": [
        "pub1",
        "pub2"
    ],
    "impressions": [
        1000,
        2000
    ],
    "clicks": [
        20,
        50
    ],
    "revenue": [
        10.0,
        25.0
    ]
})

df.to_parquet(
    "events.parquet",
    index=False
)

Upload:

gsutil cp events.parquet \
gs://vertex-demo/raw/

Verify:

gsutil ls gs://vertex-demo/raw/
Step 6: Test Dataproc BEFORE Vertex

This is critical.

If Dataproc doesn't work, Vertex won't work.

Run:

gcloud dataproc batches submit pyspark \
gs://vertex-demo/spark/feature_generation.py \
--region=us-central1 \
--deps-bucket=vertex-demo \
-- \
--input gs://vertex-demo/raw/events.parquet \
--output gs://vertex-demo/features/test_run

Monitor:

gcloud dataproc batches list \
--region=us-central1

Describe:

gcloud dataproc batches describe \
BATCH_ID \
--region=us-central1
Step 7: Verify Spark output
gsutil ls \
gs://vertex-demo/features/test_run/

Expected:

_SUCCESS

part-0000.parquet

This is the first major milestone.

If this works:

Spark Job
✓

Dataproc Serverless
✓

GCS Read
✓

GCS Write
✓
Step 8: Create BigQuery Dataset
bq mk \
--location=US \
demo_features

Verify:

bq ls
Step 9: Compile Vertex Pipeline

From repo root:

python pipelines/feature_pipeline.py

Verify:

ls pipeline_spec.json
Step 10: Upload Pipeline Spec
gsutil cp \
pipeline_spec.json \
gs://vertex-demo/templates/
Step 11: Vertex IAM

Get project number:

gcloud projects describe PROJECT_ID \
--format="value(projectNumber)"

Example:

123456789

Grant Dataproc:

gcloud projects add-iam-policy-binding PROJECT_ID \
--member=serviceAccount:123456789-compute@developer.gserviceaccount.com \
--role=roles/dataproc.editor

Grant BigQuery:

gcloud projects add-iam-policy-binding PROJECT_ID \
--member=serviceAccount:123456789-compute@developer.gserviceaccount.com \
--role=roles/bigquery.dataEditor

Grant Storage:

gcloud projects add-iam-policy-binding PROJECT_ID \
--member=serviceAccount:123456789-compute@developer.gserviceaccount.com \
--role=roles/storage.admin
Step 12: Run Vertex Pipeline
gcloud ai pipelines run \
  --project=PROJECT_ID \
  --region=us-central1 \
  --file=gs://vertex-demo/templates/pipeline_spec.json \
  --parameter-values=project_id=PROJECT_ID \
  --parameter-values=region=us-central1 \
  --parameter-values=input_path=gs://vertex-demo/raw/events.parquet \
  --parameter-values=feature_output_path=gs://vertex-demo/features/run001 \
  --parameter-values=bq_table=PROJECT_ID.demo_features.publisher_features
Step 13: Verify BigQuery
SELECT *
FROM demo_features.publisher_features
LIMIT 100;

