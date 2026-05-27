from kfp.dsl import component, Input, Output, Dataset

@component(
    base_image="python:3.11",
    packages_to_install=["pandas","pyarrow"]
)
def engineer_op(
        dataset:Input[Dataset],
        feature_dataset:Output[Dataset]
):

    import pandas as pd
    import numpy as np

    df = pd.read_parquet(dataset.path)

    df["ctr_7d"] = (
        df["clicks_7d"] /
        np.maximum(df["impressions_7d"],1)
    )

    df["rpm_7d"] = (
        df["revenue_7d"] * 1000 /
        np.maximum(df["impressions_7d"],1)
    )

    feature_date = pd.Timestamp.utcnow()

    df["feature_date"] = feature_date

    df.rename(
        columns={"publisher_id":"entity_id"},
        inplace=True
    )

    df.to_parquet(feature_dataset.path)