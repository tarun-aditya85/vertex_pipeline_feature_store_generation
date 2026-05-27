from kfp.dsl import component, Input, Output, Dataset

@component(
    base_image="python:3.11",
    packages_to_install=["pandas","pyarrow"]
)
def validate_features_op(
        dataset:Input[Dataset],
        validated_dataset:Output[Dataset]
):

    import pandas as pd

    df = pd.read_parquet(dataset.path)

    if df["ctr_7d"].isnull().any():
        raise ValueError("Null ctr")

    if df["rpm_7d"].isnull().any():
        raise ValueError("Null rpm")

    df.to_parquet(validated_dataset.path)