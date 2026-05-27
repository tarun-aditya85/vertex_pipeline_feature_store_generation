from kfp.dsl import component, Input, Output, Dataset

@component(
    base_image="python:3.11",
    packages_to_install=["pandas","pyarrow"]
)
def validate_op(
        dataset:Input[Dataset],
        validated_dataset:Output[Dataset]
):

    import pandas as pd

    df = pd.read_parquet(dataset.path)

    required = [
        "publisher_id",
        "event_date",
        "impressions",
        "clicks",
        "revenue"
    ]

    missing = set(required) - set(df.columns)

    if missing:
        raise ValueError(f"Missing columns {missing}")

    if len(df) == 0:
        raise ValueError("Empty dataset")

    df.to_parquet(validated_dataset.path)