# Vertex AI Offline Feature Store Demo

## Overview

This project demonstrates how to build a production-style offline feature store using:

- Vertex AI Pipelines
- Dataproc Serverless (Spark)
- Google Cloud Storage (GCS)
- BigQuery

The pipeline reads raw event data from GCS, generates aggregated ML features using Spark running on Dataproc Serverless, validates the features, and loads them into BigQuery as an offline feature store.

---

## Architecture

```text
                     +------------------+
                     |  Raw Events      |
                     |  GCS Parquet     |
                     +--------+---------+
                              |
                              v

                  +----------------------+
                  | Vertex AI Pipeline   |
                  +----------+-----------+
                             |
                             v

                  +----------------------+
                  | Input Validation     |
                  +----------+-----------+
                             |
                             v

                  +----------------------+
                  | Dataproc Serverless  |
                  | Spark Job            |
                  +----------+-----------+
                             |
                             |
                             +--> Filtering
                             |
                             +--> Aggregation
                             |
                             +--> Feature Engineering
                             |
                             v

                  +----------------------+
                  | Feature Parquet      |
                  | GCS                  |
                  +----------+-----------+
                             |
                             v

                  +----------------------+
                  | Feature Validation   |
                  +----------+-----------+
                             |
                             v

                  +----------------------+
                  | BigQuery             |
                  | Offline Feature Store|
                  +----------------------+
```

---

## Feature Engineering

The Spark job computes publisher-level features.

Input schema:

| Column | Type |
|----------|----------|
| event_date | DATE |
| publisher_id | STRING |
| impressions | INTEGER |
| clicks | INTEGER |
| revenue | FLOAT |

Generated features:

| Feature | Description |
|----------|----------|
| impressions_7d | Total impressions |
| clicks_7d | Total clicks |
| revenue_7d | Total revenue |
| ctr_7d | clicks/impressions |
| rpm_7d | revenue per 1000 impressions |

Output schema:

| Column |
|----------|
| entity_id |
| impressions_7d |
| clicks_7d |
| revenue_7d |
| ctr_7d |
| rpm_7d |

---

## Repository Structure

```text
.
├── components
│   ├── backup
│   │   ├── validate.py
│   │   ├── validate_features.py
│   │   └── write_bq.py
│   │
│   └── spark
│       ├── feature_generation.py
│       └── run_spark_features.py
│
├── pipelines
│   └── feature_pipeline.py
│
├── tests
│   ├── unit
│   └── integration
│
├── requirements.txt
├── cloudbuild.yaml
├── Dockerfile
└── README.md
```

---

## Prerequisites

Install:

- Python 3.11+
- gcloud CLI
- BigQuery CLI
- Vertex AI API
- Dataproc API

Authenticate:

```bash
gcloud auth login

gcloud auth application-default login
```

Set project:

```bash
gcloud config set project PROJECT_ID
```

---

## Install Dependencies

Create virtual environment:

```bash
python -m venv .venv

source .venv/bin/activate
```

Install packages:

```bash
pip install -r requirements.txt
```

---

## Enable GCP Services

```bash
gcloud services enable \
    aiplatform.googleapis.com \
    dataproc.googleapis.com \
    storage.googleapis.com \
    bigquery.googleapis.com \
    cloudbuild.googleapis.com
```

---

## Create Storage Bucket

```bash
gsutil mb -l us-central1 gs://vertex-demo
```

Create folders:

```bash
echo test > /tmp/test.txt

gsutil cp /tmp/test.txt gs://vertex-demo/raw/
gsutil cp /tmp/test.txt gs://vertex-demo/features/
gsutil cp /tmp/test.txt gs://vertex-demo/templates/
gsutil cp /tmp/test.txt gs://vertex-demo/spark/
gsutil cp /tmp/test.txt gs://vertex-demo/pipeline-root/
```

---

## Upload Spark Job

```bash
gsutil cp \
components/spark/feature_generation.py \
gs://vertex-demo/spark/
```

Verify:

```bash
gsutil ls gs://vertex-demo/spark/
```

---

## Create Sample Input Data

Generate parquet:

```python
import pandas as pd

df = pd.DataFrame({
    "event_date": ["2026-05-01"],
    "publisher_id": ["pub1"],
    "impressions": [1000],
    "clicks": [20],
    "revenue": [10.0]
})

df.to_parquet(
    "events.parquet",
    index=False
)
```

Upload:

```bash
gsutil cp events.parquet \
gs://vertex-demo/raw/events.parquet
```

---

## Test Dataproc Serverless

Run Spark directly without Vertex.

```bash
gcloud dataproc batches submit pyspark \
gs://vertex-demo/spark/feature_generation.py \
--region=us-central1 \
--deps-bucket=vertex-demo \
-- \
--input gs://vertex-demo/raw/events.parquet \
--output gs://vertex-demo/features/test_run
```

Check status:

```bash
gcloud dataproc batches list \
--region=us-central1
```

Verify output:

```bash
gsutil ls \
gs://vertex-demo/features/test_run/
```

Expected:

```text
_SUCCESS
part-00000.parquet
```

---

## Create BigQuery Dataset

```bash
bq mk \
--location=US \
demo_features
```

---

## Compile Vertex Pipeline

```bash
python pipelines/feature_pipeline.py
```

Expected:

```text
pipeline_spec.json
```

---

## Upload Pipeline Specification

```bash
gsutil cp \
pipeline_spec.json \
gs://vertex-demo/templates/
```

---

## Run Vertex Pipeline

```bash
gcloud ai pipelines run \
  --project=PROJECT_ID \
  --region=us-central1 \
  --file=gs://vertex-demo/templates/pipeline_spec.json \
  --parameter-values=project_id=PROJECT_ID \
  --parameter-values=region=us-central1 \
  --parameter-values=input_path=gs://vertex-demo/raw/events.parquet \
  --parameter-values=feature_output_path=gs://vertex-demo/features/run001 \
  --parameter-values=bq_table=PROJECT_ID.demo_features.publisher_features
```

---

## Verify Offline Feature Store

Query:

```sql
SELECT *
FROM demo_features.publisher_features
LIMIT 10;
```

Expected output:

| entity_id | impressions_7d | clicks_7d | revenue_7d | ctr_7d | rpm_7d |
|------------|------------|------------|------------|------------|------------|
| pub1 | 1000 | 20 | 10 | 0.02 | 10 |

---

## Running Tests

Execute all tests:

```bash
pytest tests/
```

Compile test:

```bash
pytest tests/integration/test_pipeline_compile.py
```

Spark feature test:

```bash
pytest tests/unit/test_feature_generation.py
```

---

## Future Enhancements

Potential production extensions:

- Vertex Feature Store registration
- Feature versioning
- Data quality metrics
- Great Expectations integration
- Dataplex integration
- Feature lineage tracking
- Scheduled pipeline execution
- CI/CD via Cloud Build
- Dataproc autoscaling policies
- Multiple feature entities (publisher, advertiser, app)

---

## Demo Flow

For a live demo:

1. Show raw parquet data in GCS.
2. Show Vertex Pipeline DAG.
3. Open Dataproc Serverless batch execution.
4. Show generated feature parquet in GCS.
5. Query BigQuery feature table.
6. Explain how training pipelines would consume the offline feature store.

This demonstrates a complete MLOps feature engineering workflow using managed GCP services.# vertex_pipeline_feature_store_generation
