# Vertex AI Offline Feature Store Demo

## Architecture

GCS
↓
Ingest
↓
Validate
↓
Filter
↓
Aggregate
↓
Feature Engineering
↓
Feature Validation
↓
BigQuery Offline Feature Store

## Compile

python pipelines/feature_pipeline.py

## Submit

gcloud ai pipelines run \
  --region=us-central1 \
  --file=pipeline_spec.json \
  --parameter-values=input_path=gs://vertex-demo/raw/events.parquet \
  --parameter-values=bq_table=demo_features.publisher_features

## Output Table

demo_features.publisher_features

Columns:

entity_id
feature_date
impressions_7d
clicks_7d
revenue_7d
ctr_7d
rpm_7d